#include "linux/linux-camera.h"

#ifdef __linux__

#include "capture-manager.h"

#include <string>
#include <linux/uinput.h>
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <stdexcept>

namespace USBCam {

    // https://lwn.net/Articles/203924/

    std::vector<Port> GetDevicesList() {
        std::vector<Port> ports;

        for (unsigned int i = 0; i < 60; i++) {
            const auto path = std::string("/dev/video") + std::to_string(i);
            const int fd = open(path.c_str(), O_RDONLY | O_NONBLOCK);

            if (fd != -1) {
                Port port;
                port.number = i;
                
                v4l2_capability cap;
                if (ioctl(fd, VIDIOC_QUERYCAP, &cap) != -1) {
                    port.name = std::string(reinterpret_cast<char*>(cap.card));
                }

                ports.push_back(port);
            } else {
                break;
            }
        }

        return ports;
    }

    LinuxCamera::LinuxCamera(uint32_t portNumber) {
        const auto path = std::string("/dev/video") + std::to_string(portNumber);
        const int fd = open(path.c_str(), O_RDONLY | O_NONBLOCK);
        if (fd == -1) {
            throw std::out_of_range("Camera does not exist at this port : " + std::to_string(portNumber));
        }

        // Get Camera capabilities
        v4l2_capability cap;
        if (ioctl(fd, VIDIOC_QUERYCAP, &cap) == -1) {
            throw std::runtime_error("Cannot get device capabilities for port : " + std::to_string(portNumber));
        }

        // Set default capture format
        v4l2_format fmt;
        fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (ioctl(fd, VIDIOC_G_FMT, &fmt) == -1) {
            throw std::runtime_error("Cannot set camera default capture format for port : " + std::to_string(portNumber));
        }
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

