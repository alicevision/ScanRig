#pragma once

#ifdef __linux__

#include <cstddef>

namespace USBCam {
    class MMapBuffer {
    public:
        /**
         * @param fd - File Descriptor describing camera optained with open()
         */
        MMapBuffer(const unsigned int fd);
        ~MMapBuffer();

        /**
         * @brief Clear buffer data
         */
        void Clear();

    private:
        void* m_start;
        size_t m_length;
    };
}

#endif // __linux__
