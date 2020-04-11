#include "linux/linux-camera.h"

#ifdef __linux__

#include "device-handling.h"

#include <string>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <vector>

#include <linux/uinput.h>
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/poll.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>

#define CLEAR(x) memset(&(x), 0, sizeof(x))

namespace USBCam {

    std::vector<Port> GetDevicesList() {
        std::vector<Port> ports;

        for (unsigned int i = 0; i < 60; i++) {
            const auto path = std::string("/dev/video") + std::to_string(i);
            const int fd = open(path.c_str(), O_RDONLY);

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

    LinuxCamera::LinuxCamera(uint32_t portNumber, std::string saveDirectory) 
        : m_fd(-1), m_id(portNumber), m_frameCount(0), m_buffers(nullptr), m_savePath(saveDirectory)
    {
        const auto path = std::string("/dev/video") + std::to_string(portNumber);
        m_fd = open(path.c_str(), O_RDWR | O_NONBLOCK);
        if (m_fd == -1) {
            throw std::invalid_argument("Camera does not exist at this port : " + std::to_string(portNumber) + " : " + std::string(strerror(errno)));
        }

        auto format = GetFormat();
        format.encoding = ICamera::FrameEncoding::MJPG;
        SetFormat(format);
        
        CreateCaptureFolders();
    }

    LinuxCamera::~LinuxCamera() {
        StopStreaming();
        delete m_buffers;
        close(m_fd);
    }

    unsigned int LinuxCamera::GetCameraId() const {
        return m_id;
    }

    std::string LinuxCamera::GetCameraName() const {
        v4l2_capability cap;
        if (ioctl(m_fd, VIDIOC_QUERYCAP, &cap) != -1) {
            return std::string(reinterpret_cast<char*>(cap.card));
        } else {
            return "Unknown";
        }
    }

    std::vector<ICamera::Format> LinuxCamera::GetSupportedFormats() const {
        std::vector<ICamera::Format> capabilities;
        
        // Get supported frame encodings
        std::vector<unsigned int> encodings;
        v4l2_fmtdesc formatDesc;
        CLEAR(formatDesc);
        formatDesc.index = 0;
        formatDesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

        while (ioctl(m_fd, VIDIOC_ENUM_FMT, &formatDesc) == 0) {
            switch (formatDesc.pixelformat) {
            case V4L2_PIX_FMT_MJPEG: encodings.push_back(V4L2_PIX_FMT_MJPEG); break;
            case V4L2_PIX_FMT_UYVY: encodings.push_back(V4L2_PIX_FMT_UYVY); break;
            default: break;
            }
            formatDesc.index++;
        }

        // Get supported frame sizes
        v4l2_frmsizeenum frameDesc;
        CLEAR(frameDesc);
        frameDesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        
        for (const auto encoding : encodings) {
            frameDesc.index = 0;
            frameDesc.pixel_format = encoding;
            
            while (ioctl(m_fd, VIDIOC_ENUM_FRAMESIZES, &frameDesc) == 0) {
                ICamera::Format cap;
                cap.id = frameDesc.index;
                cap.height = frameDesc.discrete.height;
                cap.width = frameDesc.discrete.width;
                cap.encoding = PixelFormatToFrameEncoding(frameDesc.pixel_format);
                cap.frameRate = 0;

                capabilities.push_back(cap);
                frameDesc.index++;
            }
        }

        // Get supported frame intervals
        v4l2_frmivalenum intervalDesc;
        CLEAR(intervalDesc);
        intervalDesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

        for (auto& cap : capabilities) {
            intervalDesc.width = cap.width;
            intervalDesc.height = cap.height;
            intervalDesc.pixel_format = FrameEncodingToPixelFormat(cap.encoding);

            if (ioctl(m_fd, VIDIOC_ENUM_FRAMEINTERVALS, &intervalDesc) == -1) {
                std::cerr << "Cannot get framerate : " << std::string(strerror(errno)) << std::endl;
                continue;
            }

            cap.frameRate = intervalDesc.stepwise.min.denominator;
        }

        return capabilities;
    }

    void LinuxCamera::SetFormat(const ICamera::Format& cap) {
        // Stop stream
        if (m_buffers != nullptr) {
            StopStreaming();
            delete m_buffers;
        }
        
        v4l2_format format;
        CLEAR(format);
        format.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        format.fmt.pix.pixelformat = FrameEncodingToPixelFormat(cap.encoding);
        format.fmt.pix.width = cap.width;
        format.fmt.pix.height = cap.height;

        if (ioctl(m_fd, VIDIOC_S_FMT, &format) == -1) {
            throw std::runtime_error("Cannot set camera default capture format : " + std::string(strerror(errno)));
        }

        // Start stream
        m_buffers = new MMapBuffers(m_fd);
        StartStreaming();

        // Remove the first frames as they are often corrupted
        for (size_t i = 0; i < 6; i++) {
            Wait();
            m_buffers->Dequeue();
            m_buffers->Queue();
        }

        // Handle frame structure
        m_frame.format = cap;
        m_frame.data.resize(m_buffers->GetLength());
    }

    ICamera::Format LinuxCamera::GetFormat() const {
        v4l2_format format;
        CLEAR(format);
        format.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

        if (ioctl(m_fd, VIDIOC_G_FMT, &format) == -1) {
            throw std::runtime_error("Cannot get camera capture format : " + std::string(strerror(errno)));
        }

        ICamera::Format cap;
        cap.encoding = PixelFormatToFrameEncoding(format.fmt.pix.pixelformat);
        cap.width = format.fmt.pix.width;
        cap.height = format.fmt.pix.height;
        return cap;
    }

    std::vector<ICamera::CameraSettingDetail> LinuxCamera::GetSupportedSettings() const {
        std::vector<ICamera::CameraSettingDetail> settings;

        v4l2_queryctrl queryCtrl;
        CLEAR(queryCtrl);
        queryCtrl.id = V4L2_CTRL_FLAG_NEXT_CTRL | V4L2_CTRL_FLAG_NEXT_COMPOUND;

        while (ioctl(m_fd, VIDIOC_QUERYCTRL, &queryCtrl) == 0) {
            if (!(queryCtrl.flags & V4L2_CTRL_FLAG_DISABLED)) {
                ICamera::CameraSettingDetail detail;
                detail.type = ControlIdToCameraSetting(queryCtrl.id);
                detail.max = queryCtrl.maximum;
                detail.min = queryCtrl.minimum;
                detail.default = 0; // TODO

                //if (queryCtrl.type == V4L2_CTRL_TYPE_MENU)
                //    QueryControlMenuItems(queryCtrl.id, queryCtrl.minimum, queryCtrl.maximum);

                if (detail.type == ICamera::CameraSetting::AUTO_EXPOSURE || 
                    detail.type == ICamera::CameraSetting::AUTO_ISO ||
                    detail.type == ICamera::CameraSetting::AUTO_WHITE_BALANCE) {
                    detail.min = 0;
                    detail.max = 1;
                    detail.default = 0;
                }

                if (detail.type != ICamera::CameraSetting::_UNKNOWN)
                    settings.push_back(detail);
                else
                    std::cerr << queryCtrl.name << " not supported by usbcam library" << std::endl;
            }

            queryCtrl.id |= V4L2_CTRL_FLAG_NEXT_CTRL | V4L2_CTRL_FLAG_NEXT_COMPOUND;
        }

        return settings;
    }

    bool LinuxCamera::SetSetting(CameraSetting setting, int value) {
        const int settingId = CameraSettingToControlId(setting);
        v4l2_control control;
        CLEAR(control);
        control.id = settingId;
        control.value = value;

        // Additionnal controls to fix wrong values
        switch (setting) {
        case ICamera::CameraSetting::AUTO_EXPOSURE: 
            control.value = (value == 0) ? V4L2_EXPOSURE_MANUAL : V4L2_EXPOSURE_AUTO; break;
        case ICamera::CameraSetting::AUTO_WHITE_BALANCE:
            control.value = (value == 0) ? V4L2_WHITE_BALANCE_MANUAL : V4L2_WHITE_BALANCE_AUTO; break;
        case ICamera::CameraSetting::AUTO_ISO:
            control.value = (value == 0) ? V4L2_ISO_SENSITIVITY_MANUAL : V4L2_ISO_SENSITIVITY_AUTO; break;
        default: break;
        }

        if (ioctl(m_fd, VIDIOC_S_CTRL, &control) == -1) {
            std::cerr << "Cannot set " << CameraSettingToString(setting) << " with value " << value << " : " << strerror(errno) << std::endl;
            return false;
        }
        return true;
    }

    int LinuxCamera::GetSetting(CameraSetting setting) const {
        const int settingId = CameraSettingToControlId(setting);
        v4l2_control control;
        CLEAR(control);
        control.id = settingId;
        if (ioctl(m_fd, VIDIOC_G_CTRL, &control) == -1) {
            throw std::runtime_error("Cannot set setting" + CameraSettingToString(setting) + " : " + std::string(strerror(errno)));
        }

        return control.value;
    }

    void LinuxCamera::SaveLastFrame() {
        Wait();
        m_buffers->Dequeue();

        const std::string filepath =  m_savePath + "cam" + std::to_string(m_id) + "/" + std::to_string(m_frameCount) + ".jpeg";
        int imgFile = open(filepath.c_str(), O_WRONLY | O_CREAT, 0660);
        if (imgFile == -1) {
            throw std::runtime_error("Cannot create image at : " + imgFile);
        }
        
        write(imgFile, m_buffers->GetStart(), m_buffers->GetLength());
        close(imgFile);

        m_frameCount++;
        m_buffers->Queue();
    }

    void LinuxCamera::SetSaveDirectory(const std::string& path) {
        m_savePath = path;
        CreateCaptureFolders();
    }

    const ICamera::Frame& LinuxCamera::GetLastFrame() {
        Wait();
        m_buffers->Dequeue();

        m_frame.byteWidth = m_buffers->GetLength();
        std::memcpy(m_frame.data.data(), m_buffers->GetStart(), m_buffers->GetLength());

        m_buffers->Queue();
        return m_frame;
    }

    ////////////////////////////////////////////////////////////////////
    ////////////////////////// PRIVATE METHODS /////////////////////////
    ////////////////////////////////////////////////////////////////////

    void LinuxCamera::Wait() const {
        const auto poolFlags = POLLIN | POLLRDNORM | POLLERR;
        pollfd desc { m_fd, poolFlags, 0 };
        if (poll(&desc, 1, 5000) == -1) {
            throw std::runtime_error("Pool error : " + std::string(strerror(errno)));
        }
    }

    ICamera::FrameEncoding LinuxCamera::PixelFormatToFrameEncoding(unsigned int pixelFormat) const {
        switch (pixelFormat) {
            case V4L2_PIX_FMT_MJPEG: return FrameEncoding::MJPG;
            case V4L2_PIX_FMT_UYVY: return FrameEncoding::UYVY;
            default: return FrameEncoding::_UNKNOWN;
        }
    }

    unsigned int LinuxCamera::FrameEncodingToPixelFormat(FrameEncoding encoding) const {
        switch (encoding) {
            case FrameEncoding::MJPG: return V4L2_PIX_FMT_MJPEG;
            case FrameEncoding::UYVY: return V4L2_PIX_FMT_UYVY;
            default:
                std::cerr << "Unknown encoding !" << std::endl;
                return 0;
        }
    }

    void LinuxCamera::QueryControlMenuItems(unsigned int controlId, int min, int max) const {
        v4l2_querymenu queryMenu;
        CLEAR(queryMenu);
        queryMenu.id = controlId;

        for (queryMenu.index = min; queryMenu.index <= max; queryMenu.index++) {
            if (ioctl(m_fd, VIDIOC_QUERYMENU, &queryMenu) == 0) {
                std::cout << queryMenu.name << std::endl;
            }   
        }
    }

    ICamera::CameraSetting LinuxCamera::ControlIdToCameraSetting(unsigned int controlId) const {
        switch (controlId) {
            case V4L2_CID_EXPOSURE_AUTO: return CameraSetting::AUTO_EXPOSURE;
            case V4L2_CID_AUTO_WHITE_BALANCE: return CameraSetting::AUTO_WHITE_BALANCE;
            case V4L2_CID_ISO_SENSITIVITY_AUTO: return CameraSetting::AUTO_ISO;
            case V4L2_CID_BRIGHTNESS: return CameraSetting::BRIGHTNESS;
            case V4L2_CID_CONTRAST: return CameraSetting::CONTRAST;
            case V4L2_CID_EXPOSURE_ABSOLUTE: return CameraSetting::EXPOSURE;
            case V4L2_CID_IMAGE_STABILIZATION: return CameraSetting::ENABLE_STABILIZATION;
            case V4L2_CID_WIDE_DYNAMIC_RANGE: return CameraSetting::ENABLE_HDR;
            case V4L2_CID_SATURATION: return CameraSetting::SATURATION;
            case V4L2_CID_HUE: return CameraSetting::HUE;
            case V4L2_CID_GAMMA: return CameraSetting::GAMMA;
            case V4L2_CID_WHITE_BALANCE_TEMPERATURE: return CameraSetting::WHITE_BALANCE;
            case V4L2_CID_GAIN: return CameraSetting::ISO;
            case V4L2_CID_SHARPNESS: return CameraSetting::SHARPNESS;
            default:
                std::cerr << "Unknown control ID : " << controlId << std::endl;
                return CameraSetting::_UNKNOWN;
        }
    }

    unsigned int LinuxCamera::CameraSettingToControlId(ICamera::CameraSetting setting) const {
        switch (setting) {
            case CameraSetting::AUTO_WHITE_BALANCE: return V4L2_CID_AUTO_WHITE_BALANCE;
            case CameraSetting::AUTO_EXPOSURE: return V4L2_CID_EXPOSURE_AUTO;
            case CameraSetting::AUTO_ISO: return V4L2_CID_ISO_SENSITIVITY_AUTO;
            case CameraSetting::BRIGHTNESS: return V4L2_CID_BRIGHTNESS;
            case CameraSetting::CONTRAST: return V4L2_CID_CONTRAST;
            case CameraSetting::EXPOSURE: return V4L2_CID_EXPOSURE_ABSOLUTE;
            case CameraSetting::ENABLE_STABILIZATION: return V4L2_CID_IMAGE_STABILIZATION;
            case CameraSetting::ENABLE_HDR: return V4L2_CID_WIDE_DYNAMIC_RANGE;
            case CameraSetting::SATURATION: return V4L2_CID_SATURATION;
            case CameraSetting::HUE: return V4L2_CID_HUE;
            case CameraSetting::GAMMA: return V4L2_CID_GAMMA;
            case CameraSetting::WHITE_BALANCE: return V4L2_CID_WHITE_BALANCE_TEMPERATURE;
            case CameraSetting::ISO: return V4L2_CID_ISO_SENSITIVITY;
            case CameraSetting::SHARPNESS: return V4L2_CID_SHARPNESS;
            default:
                std::cerr << "Unknown camera setting !" << std::endl;
                return 0;
        }
    }

    void LinuxCamera::StartStreaming() {
        int type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (ioctl(m_fd, VIDIOC_STREAMON, &type) == -1) {
            throw std::runtime_error("Cannot start streaming : " + std::string(strerror(errno)));
        }
    }

    void LinuxCamera::StopStreaming() {
        int type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        if (ioctl(m_fd, VIDIOC_STREAMOFF, &type) == -1) {
            throw std::runtime_error("Cannot stop streaming : " + std::string(strerror(errno)));
        }
    }

    void LinuxCamera::CreateCaptureFolders() {
        m_savePath += "/"; // TODO check before adding if last character / exist
        mkdir(m_savePath.c_str(), S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
        const std::string path = m_savePath + "cam" + std::to_string(m_id);
        mkdir(path.c_str(), S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
    }
}

#endif // __linux__

