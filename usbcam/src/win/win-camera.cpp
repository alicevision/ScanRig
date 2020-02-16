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

    std::vector<Port> GetDevicesList() {
        auto filteredSourceInfos = single_threaded_vector<MediaFrameSourceInfo>();
        const auto sourceGroups = MediaFrameSourceGroup::FindAllAsync().get();
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

        return GetDevicesInfo(filteredSourceInfos);
    }

    WinCamera::WinCamera(uint32_t portNumber) {

    }

    WinCamera::~WinCamera() {}

    std::vector<Camera::Capabilities> WinCamera::GetCapabilities() const {
        std::vector<Camera::Capabilities> capabilities;
        return capabilities;
    }
}

#endif // _WIN32
