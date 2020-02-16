#include "win/win-camera.h"

#ifdef _WIN32

#include <iostream>

#include "capture-manager.h"

namespace USBCam {
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

    WinCamera::WinCamera(uint32_t portNumber) : m_sourceGroups(nullptr), m_sourceInfo(nullptr), m_reader(nullptr) {
        // Get camera
        m_sourceGroups = MediaFrameSourceGroup::FindAllAsync().get();
        auto filteredGroups = GetFilteredSourceGroupList(m_sourceGroups);
        m_sourceInfo = filteredGroups.GetAt(portNumber); 
        if (m_sourceInfo == nullptr) {
            throw std::out_of_range(std::string("Camera does not exist at this index : " + portNumber));
        }

        // Set default settings
        auto settings = MediaCaptureInitializationSettings();
        settings.SourceGroup(m_sourceInfo.SourceGroup());
        settings.PhotoCaptureSource(PhotoCaptureSource::Auto);
        settings.StreamingCaptureMode(StreamingCaptureMode::Video);
        
        // Init camera
        m_capture.InitializeAsync(settings).get(); // FIXME throws an exeption but cannot be catched
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

    std::vector<ICamera::Capabilities> WinCamera::GetCapabilities() const {
        std::vector<ICamera::Capabilities> capabilities;
        auto mediaDescriptionIter = m_sourceInfo.VideoProfileMediaDescription().First();
        
        int idx = 0;
        while (mediaDescriptionIter.HasCurrent()) {
            const auto format = mediaDescriptionIter.Current();

            ICamera::Capabilities cap;
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

    FrameEncoding WinCamera::SubTypeToFrameEncoding(const std::string& subType) const {
        if (subType == "NV12")
            return FrameEncoding::NV12;
        if (subType == "MJPG")
            return FrameEncoding::MJPG;

        return FrameEncoding::_UNKNOWN;
    }

    void WinCamera::StartPreview() {
        // start Preview to get the 3A running and wait for convergence.
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

    void WinCamera::TakePicture(std::string saveFolderPath) const {
        WCHAR ExePath[MAX_PATH] = { 0 };
        if (GetModuleFileNameW(NULL, ExePath, _countof(ExePath)) == 0)
        {
            std::cout << "\nError getting the path to executable, defaulting output folder to C:\\test";
            wcscpy_s(ExePath, L"C:\\");
        }

        auto file = Windows::Storage::StorageFile::GetFileFromPathAsync(ExePath).get();
        auto folderRoot = file.GetParentAsync().get();
        auto folder = folderRoot.CreateFolderAsync(L"camera0\\", CreationCollisionOption::OpenIfExists).get();
        auto saveFile = folder.CreateFileAsync(L"pic.png", CreationCollisionOption::GenerateUniqueName).get();

        m_capture.CapturePhotoToStorageFileAsync(ImageEncodingProperties::CreatePng(), saveFile).get();
    }
}

#endif // _WIN32
