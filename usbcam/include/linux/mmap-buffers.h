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
        MMapBuffers(const unsigned int fd, const unsigned int count = 1);
        ~MMapBuffers();

        /**
         * @brief Clear buffer data
         */
        void Clear();

        /**
         * @brief Queue the next buffer
         */
        void Queue();

        /**
         * @brief Dequeue the last buffer
         */
        void Dequeue();

        unsigned int GetLength() { return m_buffer.info.length; }
        void* GetStart() { return m_buffer.start; }

    private:
        struct V4L2Buffer {
            v4l2_buffer info;
            void* start;
        };

        V4L2Buffer m_buffer; // TEMP use a std::vector
        unsigned int m_fd;
    };
}

#endif // __linux__
