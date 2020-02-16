#pragma once

#include <vector>
#include <stdint.h>
#include <string>

#include "i-camera.h"

namespace USBCam {
    /**
     * @brief Identify a device connected to the computer
     */
    struct Port {
        uint32_t number;
        std::string name;
    };

    /**
     * @brief Get the devices connected to the computer
     * @return std::vector<Port> 
     */
    std::vector<Port> GetDevicesList();

    /**
     * @brief Handles multiple camera creation, multi-threaded capture and image saving
     */
    class CaptureManager {
    public:
        CaptureManager(std::vector<uint32_t> portNumbers);
        ~CaptureManager();

        ICamera* GetCam(uint32_t number) { return m_cams.at(number); }

    private:
        std::vector<ICamera*> m_cams;
    };
}
