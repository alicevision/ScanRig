#include "linux/mmap-buffers.h"

#ifdef __linux__

#include <string>
#include <cstring>
#include <stdexcept>

#include <linux/uinput.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>

namespace USBCam {
    MMapBuffers::MMapBuffers(const unsigned int fd, const unsigned int count) {
        // Request buffers
        v4l2_requestbuffers bufrequest;
        bufrequest.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        bufrequest.memory = V4L2_MEMORY_MMAP;
        bufrequest.count = 1; // TEMP

        if (ioctl(fd, VIDIOC_REQBUFS, &bufrequest) == -1) {
            throw std::runtime_error("Cannot request new buffer : " + std::string(strerror(errno)));
        }

        // Allocate buffers
        memset(&(m_buffer.info), 0, sizeof(m_buffer.info)); // Clear
        m_buffer.info.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        m_buffer.info.memory = V4L2_MEMORY_MMAP;
        m_buffer.info.index = 0; // Only one buffer for now

        if (ioctl(fd, VIDIOC_QUERYBUF, &m_buffer.info) == -1) {
            throw std::runtime_error("Cannot allocate buffer : " + std::string(strerror(errno)));
        }

        // Map buffer to memory
        m_buffer.start = mmap(
            NULL,
            m_buffer.info.length,
            PROT_READ | PROT_WRITE,
            MAP_SHARED,
            fd,
            m_buffer.info.m.offset
        );

        if (m_buffer.start == MAP_FAILED) {
            throw std::runtime_error("Cannot map buffer : " + std::string(strerror(errno)));
        }

        Clear();
    }

    MMapBuffers::~MMapBuffers() {
        munmap(m_buffer.start, m_buffer.info.length);
    }

    void MMapBuffers::Clear() {
        memset(m_buffer.start, 0, m_buffer.info.length);
    }
}

#endif // __linux__
