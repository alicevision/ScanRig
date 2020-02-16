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
            idx++;
            const auto currSource = source.Current();

            Port port;
            port.number = idx;
            port.name = to_string(currSource.SourceGroup().DisplayName());
            ports.push_back(port);

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

    WinCamera::WinCamera(uint32_t portNumber) : m_sourceInfo(nullptr) {
        auto sourceGroups = MediaFrameSourceGroup::FindAllAsync().get(); // TODO might need to keep ref to this + See if possible to get by id
        auto filteredGroups = GetFilteredSourceGroupList(sourceGroups);
        m_sourceInfo = filteredGroups.GetAt(portNumber);
        
        if (m_sourceInfo == nullptr) {
            throw std::out_of_range(std::string("Camera does not exist at this index : " + portNumber));
        }

        auto settings = MediaCaptureInitializationSettings();
        settings.SourceGroup(m_sourceInfo.SourceGroup());
        settings.PhotoCaptureSource(PhotoCaptureSource::Auto);
        settings.StreamingCaptureMode(StreamingCaptureMode::Video);
        
    }

    WinCamera::~WinCamera() {
        m_sourceInfo = nullptr;
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
            // TODO get encoding
            capabilities.push_back(cap);

            idx++;
            mediaDescriptionIter.MoveNext();
        }

        return capabilities;
    }
}

#endif // _WIN32
