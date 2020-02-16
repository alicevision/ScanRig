#pragma once

#include <vector>
#include <string>
#include <stdint.h>

namespace USBCam {
    /**
     * @brief Data format supported by the camera
     */
    enum class FrameEncoding {
        YUYV,
        MPEG
    };

    /**
     * @brief Abstract Interface to control a USB Camera under any OS.
     */
    class ICamera {
    public:
        /**
         * @brief Capture settings supported by the camera
         */
        struct Capabilities {
            uint32_t id;
            uint32_t frameRate;
            uint32_t width;
            uint32_t height;
            FrameEncoding encoding;
        };

        virtual ~ICamera() {};

        /**
         * @brief Get the record values supported by the camera
         * @return std::vector<Capabilities> 
         */
        virtual std::vector<Capabilities> GetCapabilities() const = 0;
    };
}
