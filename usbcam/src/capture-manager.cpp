#include "capture-manager.h"

#include <iostream>

#include "win/win-camera.h"

namespace USBCam {
    CaptureManager::CaptureManager(std::vector<uint32_t> portNumbers) {
        try {
            for (const auto port : portNumbers) {
            #ifdef _WIN32
                m_cams.push_back(new WinCamera(port));
            #elif __linux__
                // TODO
            #endif
            }
        } catch(const std::exception& e) {
            std::cerr << "[CaptureManager] Cannot control camera : " << e.what() << std::endl;
            for (auto cam : m_cams) {
                delete cam;
            }
            throw;
        } catch(...) {
            std::cerr << "[CaptureManager] Unknown exception !" << std::endl;
        }
    }

    CaptureManager::~CaptureManager() {
        for (auto cam : m_cams) {
            delete cam;
        }
    }
}
