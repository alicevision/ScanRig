#include "linux/linux-camera.h"

#ifdef __linux__

#include "capture-manager.h"

namespace USBCam {
    std::vector<Port> GetDevicesList() {
        std::vector<Port> ports;
        return ports;
    }

    std::vector<ICamera::Capabilities> LinuxCamera::GetCapabilities() const {
        std::vector<ICamera::Capabilities> capabilities;
        return capabilities;
    }

    void LinuxCamera::SetFormat(uint32_t id) {

    }

    void LinuxCamera::TakeAndSavePicture() const {

    }
}

#endif // __linux__

