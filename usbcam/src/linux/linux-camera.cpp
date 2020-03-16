#include "linux/linux-camera.h"

#ifdef __linux__

#include "capture-manager.h"

#include <string>
#include <cstring>
#include <linux/uinput.h>
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <stdexcept>
#include <errno.h>

#define CLEAR(x) memset(&(x), 0, sizeof(x))

namespace USBCam {

    // https://lwn.net/Articles/203924/
    // http://jwhsmith.net/2014/12/capturing-a-webcam-stream-using-v4l2/
    // https://chromium.googlesource.com/chromium/src.git/+/40.0.2214.91/media/video/capture/linux/video_capture_device_linux.cc

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

    LinuxCamera::LinuxCamera(uint32_t portNumber) : m_fd(-1) {
        const auto path = std::string("/dev/video") + std::to_string(portNumber);
        m_fd = open(path.c_str(), O_RDWR);
        if (m_fd == -1) {
            throw std::out_of_range("Camera does not exist at this port : " + std::to_string(portNumber) + " : " + std::string(strerror(errno)));
        }

        // Get Camera capabilities
        v4l2_capability cap;
        if (ioctl(m_fd, VIDIOC_QUERYCAP, &cap) == -1) {
            throw std::runtime_error("Cannot get device capabilities for port : " + std::to_string(portNumber) + " : "+ std::string(strerror(errno)));
        }

        // Set default capture format
        v4l2_format format;
        CLEAR(format);
        format.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        format.fmt.pix.pixelformat = V4L2_PIX_FMT_MJPEG;
        format.fmt.pix.width = 800;
        format.fmt.pix.height = 640;
        if (ioctl(m_fd, VIDIOC_S_FMT, &format) == -1) {
            throw std::runtime_error("Cannot set camera default capture format for port : " + std::to_string(portNumber) + " : "+ std::string(strerror(errno)));
        }
    }

    LinuxCamera::~LinuxCamera() {

    }

    std::vector<ICamera::Capabilities> LinuxCamera::GetCapabilities() const {
        std::vector<ICamera::Capabilities> capabilities;
        
        // Get supported frame encodings
        std::vector<FrameEncoding> encodings;
        v4l2_fmtdesc formatDesc;
        CLEAR(formatDesc);
        formatDesc.index = 0;
        formatDesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

        while (ioctl(m_fd, VIDIOC_ENUM_FMT, &formatDesc) == 0) {
            formatDesc.index++;
            switch (formatDesc.pixelformat) {
            case V4L2_PIX_FMT_MJPEG:
                encodings.push_back(FrameEncoding::MJPG);
                break;

            case V4L2_PIX_FMT_UYVY:
                encodings.push_back(FrameEncoding::UYVY);
                break;
            
            default:
                encodings.push_back(FrameEncoding::_UNKNOWN);
                break;
            }
        }

        // Get supported frame sizes
        v4l2_frmsizeenum frameDesc;
        CLEAR(frameDesc);
        frameDesc.index = 0;
        frameDesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

        while (ioctl(m_fd, VIDIOC_ENUM_FRAMESIZES, &frameDesc) == 0) {
            frameDesc.index++;
        }

        // Get supported frame intervals
        v4l2_frmivalenum intervalDesc;
        CLEAR(intervalDesc);
        intervalDesc.index = 0;
        intervalDesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

        while (ioctl(m_fd, VIDIOC_ENUM_FRAMEINTERVALS, &intervalDesc) == 0) {
            intervalDesc.index++;
        }
        
        return capabilities;
    }

    void LinuxCamera::SetFormat(uint32_t id) {

    }

    void LinuxCamera::TakeAndSavePicture() const {

    }
}

#endif // __linux__

