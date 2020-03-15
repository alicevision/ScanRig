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

        /**
         * @brief Get a camera
         * 
         * @param number - The index in the array of camera
         * @return ICamera* 
         */
        ICamera* GetCam(uint32_t number) { return m_cams.at(number); }

        /**
         * @brief Save a picture from each cameras (not multithreaded yet)
         */
        void TakeAndSavePictures() const;

        /**
         * @brief Set the Capture format of the usb cams
         * 
         * @param id 
         */
        void SetFormat(uint32_t id);

    private:
        std::vector<ICamera*> m_cams;
    };
}
