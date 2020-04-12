#pragma once

#include <string>
#include <memory>
#include <vector>

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
     * @brief Create a new Camera. You own it.
     * 
     * @param portNumber 
     * @return std::unique_ptr<ICamera>
     */
    std::unique_ptr<ICamera> CreateCamera(uint32_t portNumber, std::string saveDirectory = "./capture");
}
