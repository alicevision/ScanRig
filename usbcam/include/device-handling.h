#pragma once

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
     * @brief Create a new Camera
     * @note You must delete the object when you are done
     * 
     * @param portNumber 
     * @return ICamera* 
     */
    ICamera* CreateCamera(uint32_t portNumber);
}
