#include "win/win-camera.h"

#ifdef _WIN32

#include <iostream>
#include <filesystem>

#include "device-handling.h"

namespace USBCam {

    /////////////////////////////////////////////////////////////////////////
    /////////////////////////// Non-Class functions /////////////////////////
    /////////////////////////////////////////////////////////////////////////

    std::vector<Port> GetDevicesInfo(const IVector<MediaFrameSourceInfo>& filteredSources) {
        std::vector<Port> ports;
        auto source = filteredSources.First();
        
        unsigned int idx = 0;
        while (source.HasCurrent()) {
            const auto currSource = source.Current();

            Port port;
            port.number = idx;
            port.name = to_string(currSource.SourceGroup().DisplayName());
            ports.push_back(port);

            idx++;
            source.MoveNext();
        }
        
        return ports;
    }

    IVector<MediaFrameSourceInfo> GetFilteredSourceGroupList(const IVectorView<MediaFrameSourceGroup>& sourceGroups) {
        auto filteredSourceInfos = single_threaded_vector<MediaFrameSourceInfo>();
        auto sourceGroupIter = sourceGroups.First();

        while (sourceGroupIter.HasCurrent()) {
            auto sourceInfos = sourceGroupIter.Current().SourceInfos();
            auto sourceInfoIter = sourceInfos.First();

            while (sourceInfoIter.HasCurrent()) {
                if ((sourceInfoIter.Current().MediaStreamType() == MediaStreamType::Photo
                    || sourceInfoIter.Current().MediaStreamType() == MediaStreamType::VideoPreview
                    || sourceInfoIter.Current().MediaStreamType() == MediaStreamType::VideoRecord)
                    && sourceInfoIter.Current().SourceKind() == MediaFrameSourceKind::Color)
                {
                    filteredSourceInfos.Append(sourceInfoIter.Current());
                }
                sourceInfoIter.MoveNext();
            }
            sourceGroupIter.MoveNext();
        }

        return filteredSourceInfos;
    }

    std::vector<Port> GetDevicesList() {
        return GetDevicesInfo(GetFilteredSourceGroupList(MediaFrameSourceGroup::FindAllAsync().get()));
    }

    /////////////////////////////////////////////////////////////////////////
    ////////////////////////////// Public Methods ///////////////////////////
    /////////////////////////////////////////////////////////////////////////

    WinCamera::WinCamera(uint32_t portNumber) 
    : m_sourceGroups(nullptr), m_sourceInfo(nullptr), m_reader(nullptr), m_portNumber(portNumber) {
        // Get camera
        m_sourceGroups = MediaFrameSourceGroup::FindAllAsync().get();
        auto filteredGroups = GetFilteredSourceGroupList(m_sourceGroups);

        try {
            m_sourceInfo = filteredGroups.GetAt(portNumber);
        } catch (winrt::hresult_error const& ex) {
            throw std::out_of_range("Camera does not exist at this port : " + std::to_string(portNumber) + " : " + winrt::to_string(ex.message()));
        }

        // Set default settings
        auto settings = MediaCaptureInitializationSettings();
        settings.SourceGroup(m_sourceInfo.SourceGroup());
        settings.PhotoCaptureSource(PhotoCaptureSource::Auto);
        settings.StreamingCaptureMode(StreamingCaptureMode::Video);
        
        // Init camera
        m_capture.InitializeAsync(settings).get(); // FIXME throws an exception but cannot be catched 'Device do not exist'

        StartPreview();
    }

    WinCamera::~WinCamera() {
        m_sourceGroups = nullptr;
        m_sourceInfo = nullptr;
        m_reader.StopAsync().get();
        m_reader.Close();
        m_reader = nullptr;
        m_capture.Close();
        m_capture = nullptr;
    }

    std::vector<ICamera::Format> WinCamera::GetSupportedFormats() const {
        std::vector<ICamera::Format> capabilities;
        auto mediaDescriptionIter = m_sourceInfo.VideoProfileMediaDescription().First();
        
        int idx = 0;
        while (mediaDescriptionIter.HasCurrent()) {
            const auto format = mediaDescriptionIter.Current();

            ICamera::Format cap;
            cap.height = format.Height();
            cap.width = format.Width();
            cap.frameRate = static_cast<uint32_t>(format.FrameRate());
            cap.id = idx;
            cap.encoding = SubTypeToFrameEncoding(to_string(format.Subtype()));
            capabilities.push_back(cap);

            idx++;
            mediaDescriptionIter.MoveNext();
        }

        return capabilities;
    }

    ICamera::Format WinCamera::GetFormat() {
        ICamera::Format cap;
        return cap;
    }

    void WinCamera::SetFormat(const ICamera::Format& cap) {
        auto frameSource = m_capture.FrameSources().Lookup(m_sourceInfo.Id());
        frameSource.SetFormatAsync(frameSource.SupportedFormats().GetAt(cap.id)).get();
    }

    std::vector<ICamera::CameraSettingDetail> WinCamera::GetSupportedSettings() const {
        std::vector<CameraSettingDetail> settings;
        return settings;
    }

    bool WinCamera::SetSetting(ICamera::CameraSetting setting, int value) {
        switch (setting) {
        case CameraSetting::EXPOSURE:           return m_capture.VideoDeviceController().Exposure().TrySetValue(value);
        case CameraSetting::BRIGHTNESS:         return m_capture.VideoDeviceController().Brightness().TrySetValue(value);
        case CameraSetting::CONTRAST:           return m_capture.VideoDeviceController().Contrast().TrySetValue(value);
        case CameraSetting::HUE:                return m_capture.VideoDeviceController().Hue().TrySetValue(value);
        case CameraSetting::WHITE_BALANCE:      return m_capture.VideoDeviceController().WhiteBalance().TrySetValue(value);
        case CameraSetting::AUTO_WHITE_BALANCE: return m_capture.VideoDeviceController().WhiteBalance().TrySetAuto(value >= 1);
        case CameraSetting::ISO: {
            m_capture.VideoDeviceController().IsoSpeedControl().SetValueAsync(value);
            return true;
        }
        default:
            return false;
        }
    }

    int WinCamera::GetSetting(ICamera::CameraSetting setting) {
        switch (setting) {
        case CameraSetting::ISO: return m_capture.VideoDeviceController().IsoSpeedControl().Value();
        case CameraSetting::EXPOSURE: {
            double value = 0;
            m_capture.VideoDeviceController().Exposure().TryGetValue(value);
            return static_cast<int>(value);
        }
        case CameraSetting::BRIGHTNESS: {
            double value = 0;
            m_capture.VideoDeviceController().Brightness().TryGetValue(value); 
            return static_cast<int>(value);
        }
        case CameraSetting::CONTRAST: {
            double value = 0;
            m_capture.VideoDeviceController().Contrast().TryGetValue(value); 
            return static_cast<int>(value);
        }
        case CameraSetting::HUE: {
            double value = 0;
            m_capture.VideoDeviceController().Hue().TryGetValue(value); 
            return static_cast<int>(value);
        }
        case CameraSetting::AUTO_WHITE_BALANCE: {
            bool value = false;
            m_capture.VideoDeviceController().WhiteBalance().TryGetAuto(value); 
            return value ? 1 : 0;
        }
        case CameraSetting::WHITE_BALANCE: {
            double value = 0;
            m_capture.VideoDeviceController().WhiteBalance().TryGetValue(value); 
            return static_cast<int>(value);
        }
        default: 
            return 0;
        }
    }

    void WinCamera::TakeAndSavePicture() {
        auto path = std::filesystem::current_path();
        auto folderRoot = Windows::Storage::StorageFolder::GetFolderFromPathAsync(path.c_str()).get();
        auto folder = folderRoot.CreateFolderAsync(to_hstring(std::string("cam_") + std::to_string(m_portNumber)), CreationCollisionOption::OpenIfExists).get();
        auto saveFile = folder.CreateFileAsync(L"01.png", CreationCollisionOption::GenerateUniqueName).get();

        m_capture.CapturePhotoToStorageFileAsync(ImageEncodingProperties::CreatePng(), saveFile).get();
    }

    /////////////////////////////////////////////////////////////////////////
    ///////////////////////////// Private Methods ///////////////////////////
    /////////////////////////////////////////////////////////////////////////

    ICamera::FrameEncoding WinCamera::SubTypeToFrameEncoding(const std::string& subType) const {
        if (subType == "NV12")
            return FrameEncoding::NV12;
        if (subType == "MJPG")
            return FrameEncoding::MJPG;

        return FrameEncoding::_UNKNOWN;
    }

    void WinCamera::StartPreview() {
        // Start Preview to get the 3A running and wait for convergence.
        MediaFrameSource previewframeSource(nullptr);
        MediaStreamType streamTypelookup = MediaStreamType::VideoPreview;

        // Try to find the suitable pin where 3A will be running.
        // Start by looking for a preview pin , if not found look for record pin 
        // However exit the loop when preview and record pins are not available as just running the photo pin cannot converge 3A
        while ((previewframeSource == nullptr) && (streamTypelookup != MediaStreamType::Photo)) {
            auto frameSourceIter = m_capture.FrameSources().First();
            // If there is no preview pin, find a record pin
            while (frameSourceIter.HasCurrent()) {
                auto frameSource = frameSourceIter.Current().Value();
                if (frameSource.Info().MediaStreamType() == streamTypelookup)
                {
                    previewframeSource = frameSource;
                    break;
                }
                frameSourceIter.MoveNext();
            }
            streamTypelookup = (streamTypelookup == MediaStreamType::VideoPreview) ? MediaStreamType::VideoRecord : MediaStreamType::Photo;
        }

        m_reader = m_capture.CreateFrameReaderAsync(previewframeSource).get();
        m_reader.AcquisitionMode(MediaFrameReaderAcquisitionMode::Realtime);
        m_reader.StartAsync().get();
    }
}

#endif // _WIN32
