#pragma once

#ifdef __linux__

#include <cstddef>
#include <vector>

#include <linux/videodev2.h>

namespace USBCam {
    class MMapBuffers {
    public:
        /**
         * @param fd - File Descriptor describing camera optained with open()
         * @param count - Number of buffers to use
         */
        MMapBuffers(const unsigned int fd, const unsigned int count = 5);
        ~MMapBuffers();

        /**
         * @brief Clear all buffers data
         */
        void Clear();

        /**
         * @brief Queue the last dequeued buffer
         */
        void Queue();

        /**
         * @brief Dequeue the next filled buffer
         */
        void Dequeue();

        /**
         * @brief Get the length of the last dequeued buffer
         * 
         * @return unsigned int 
         */
        unsigned int GetLength() { return m_buffers.at(m_lastDequeued).info.length; }
        void* GetStart() { return m_buffers.at(m_lastDequeued).start; }

    private:
        struct V4L2Buffer {
            v4l2_buffer info;
            void* start;
        };

        std::vector<V4L2Buffer> m_buffers;
        unsigned int m_bufferCount;
        unsigned int m_lastDequeued;
        unsigned int m_fd;
    };
}

#endif // __linux__
