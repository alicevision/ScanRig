#include "device-handling.h"

#include "win/win-camera.h"
#include "linux/linux-camera.h"

#include <iostream>

namespace USBCam {
    std::unique_ptr<ICamera> CreateCamera(uint32_t port) {
        try {
            #ifdef _WIN32
                return std::unique_ptr<ICamera>(new WinCamera(port));
            #elif __linux__
                return std::unique_ptr<ICamera>(new LinuxCamera(port));
            #endif
        } catch(const std::exception& e) {
            std::cerr << "[CreateCamera] " << e.what() << std::endl;
            throw;
        } catch(...) {
            std::cerr << "[CreateCamera] Unknown exception !" << std::endl;
            throw;
        }
    }
}
