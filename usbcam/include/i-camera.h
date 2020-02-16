#pragma once

#include <vector>
#include <string>
#include <stdint.h>

namespace USBCam {
    /**
     * @brief Data format supported by the camera
     */
    enum class FrameEncoding {
        _UNKNOWN,
        YUY2,
        MJPG,
        NV12
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
            uint32_t id = 0;
            uint32_t frameRate = 0;
            uint32_t width = 0;
            uint32_t height = 0;
            FrameEncoding encoding = FrameEncoding::_UNKNOWN;
        };

        virtual ~ICamera() {};

        /**
         * @brief Get the record values supported by the camera
         * @return std::vector<Capabilities> 
         */
        virtual std::vector<Capabilities> GetCapabilities() const = 0;

        /**
         * @brief Take a picture and save it in current working directory
         */
        virtual void TakeAndSavePicture() const = 0;
    };
}
