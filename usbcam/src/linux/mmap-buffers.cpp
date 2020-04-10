#include "linux/mmap-buffers.h"

#ifdef __linux__

#include <string>
#include <cstring>
#include <stdexcept>
#include <iostream>

#include <linux/uinput.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>

namespace USBCam {
    MMapBuffers::MMapBuffers(const unsigned int fd, const unsigned int count) : m_fd(fd), m_bufferCount(count), m_lastDequeued(count) {
        // Request buffers
        v4l2_requestbuffers bufrequest;
        bufrequest.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        bufrequest.memory = V4L2_MEMORY_MMAP;
        bufrequest.count = count;

        if (ioctl(fd, VIDIOC_REQBUFS, &bufrequest) == -1) {
            throw std::runtime_error("Cannot request buffers : " + std::string(strerror(errno)));
        }

        // Allocate buffers
        m_buffers.resize(count);
        unsigned int index = 0;
        for (auto& buffer : m_buffers) {
            memset(&buffer.info, 0, sizeof(buffer.info)); // Clear structure
            buffer.info.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
            buffer.info.memory = V4L2_MEMORY_MMAP;
            buffer.info.index = index;

            if (ioctl(fd, VIDIOC_QUERYBUF, &buffer.info) == -1) {
                throw std::runtime_error("Cannot allocate buffer : " + std::string(strerror(errno)));
            }

            // Map buffer to memory
            buffer.start = mmap(
                NULL,
                buffer.info.length,
                PROT_READ | PROT_WRITE,
                MAP_SHARED,
                fd,
                buffer.info.m.offset
            );

            if (buffer.start == MAP_FAILED) {
                throw std::runtime_error("Cannot map buffer : " + std::string(strerror(errno)));
            }

            index++;
        }

        Clear();
        QueueAll();
    }

    MMapBuffers::~MMapBuffers() {
        for (auto& buffer : m_buffers) {
            munmap(buffer.start, buffer.info.length);
        }
        
        // Reset camera buffer state
        v4l2_requestbuffers bufrequest;
        bufrequest.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;
        bufrequest.memory = V4L2_MEMORY_MMAP;
        bufrequest.count = 0;
        if (ioctl(m_fd, VIDIOC_REQBUFS, &bufrequest) == -1) {
            std::cerr << "Cannot reset buffers : " << strerror(errno) << std::endl;
        }
    }

    void MMapBuffers::Clear() {
        for (auto& buffer : m_buffers) {
            memset(buffer.start, 0, buffer.info.length);
        }
    }

    void MMapBuffers::QueueAll() {
        for (auto& buffer : m_buffers) {
            if (ioctl(m_fd, VIDIOC_QBUF, &buffer.info) == -1) {
                throw std::runtime_error("Cannot queue buffer : " + std::string(strerror(errno)));
            }
        }
    }

    void MMapBuffers::Queue() {
        if (ioctl(m_fd, VIDIOC_QBUF, &m_buffers.at(m_lastDequeued).info) == -1) {
            throw std::runtime_error("Cannot queue buffer : " + std::string(strerror(errno)));
        }
    }

    void MMapBuffers::Dequeue() {
        if (m_lastDequeued + 1 >= m_bufferCount) {
            m_lastDequeued = 0;
        } else {
            m_lastDequeued++;
        }
        
        // TODO check if einbusy, if so retry a few times
        if (ioctl(m_fd, VIDIOC_DQBUF, &m_buffers.at(m_lastDequeued).info) == -1) {
            throw std::runtime_error("Cannot dequeue buffer : " + std::string(strerror(errno)));
        }
    }
}

#endif // __linux__
