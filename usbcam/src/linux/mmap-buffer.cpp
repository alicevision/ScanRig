#include "linux/mmap-buffer.h"

#ifdef __linux__

#include <string>
#include <cstring>
#include <stdexcept>

#include <linux/uinput.h>
#include <linux/videodev2.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>

namespace USBCam {
    MMapBuffer::MMapBuffer(const unsigned int fd) {
        // Request buffers
        v4l2_requestbuffers bufrequest;
        bufrequest.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        bufrequest.memory = V4L2_MEMORY_MMAP;
        bufrequest.count = 1;

        if (ioctl(fd, VIDIOC_REQBUFS, &bufrequest) == -1) {
            throw std::runtime_error("Cannot request new buffer : " + std::string(strerror(errno)));
        }

        // Allocate buffers
        v4l2_buffer bufferinfo;
        memset(&(bufferinfo), 0, sizeof(bufferinfo)); // Clear
        bufferinfo.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        bufferinfo.memory = V4L2_MEMORY_MMAP;
        bufferinfo.index = 0; // Only one buffer for now

        if (ioctl(fd, VIDIOC_QUERYBUF, &bufferinfo) == -1) {
            throw std::runtime_error("Cannot allocate buffer : " + std::string(strerror(errno)));
        }

        // Map buffer to memory
        m_start = mmap(
            NULL,
            bufferinfo.length,
            PROT_READ | PROT_WRITE,
            MAP_SHARED,
            fd,
            bufferinfo.m.offset
        );

        if (m_start == MAP_FAILED) {
            throw std::runtime_error("Cannot map buffer : " + std::string(strerror(errno)));
        }
        m_length = bufferinfo.length;

        Clear();
    }

    MMapBuffer::~MMapBuffer() {
        munmap(m_start, m_length);
    }

    void MMapBuffer::Clear() {
        memset(m_start, 0, m_length);
    }
}

#endif // __linux__
