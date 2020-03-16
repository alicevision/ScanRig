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

    private:
        struct V4L2Buffer {
            v4l2_buffer info;
            void* start;
        };

        V4L2Buffer m_buffer;
    };
}

#endif // __linux__
