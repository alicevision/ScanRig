#include "linux/linux-camera.h"

#ifdef __linux__

#include "capture-manager.h"

#include <string>
#include <linux/videodev2.h>
#include <fcntl.h>

namespace USBCam {

    // https://lwn.net/Articles/203924/

    std::vector<Port> GetDevicesList() {
        std::vector<Port> ports;

        for (unsigned int i = 0; i < 60; i++) {
            const auto path = std::string("/dev/video") + std::to_string(i);
            int fd = open(path.c_str(), O_RDONLY);
            if (fd != -1) {
                Port port;
                port.number = i;
                ports.push_back(port);
            } else {
                break;
            }
        }

        return ports;
    }

    LinuxCamera::LinuxCamera(uint32_t portNumber) {

    }

    LinuxCamera::~LinuxCamera() {

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

