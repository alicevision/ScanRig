#include "capture-manager.h"

#include <iostream>

#include "win/win-camera.h"
#include "linux/linux-camera.h"

namespace USBCam {
    CaptureManager::CaptureManager(std::vector<uint32_t> portNumbers) {
        try {
            for (const auto port : portNumbers) {
            #ifdef _WIN32
                m_cams.push_back(new WinCamera(port));
            #elif __linux__
                m_cams.push_back(new LinuxCamera(port));
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
            for (auto cam : m_cams) {
                delete cam;
            }
        }
    }

    CaptureManager::~CaptureManager() {
        for (auto cam : m_cams) {
            delete cam;
        }
    }

    void CaptureManager::TakeAndSavePictures() const {
        for (const auto cam : m_cams) {
            cam->TakeAndSavePicture();
        }
    }

    void CaptureManager::SetFormat(uint32_t id) {
        for (const auto cam : m_cams) {
            // cam->SetFormat(id);
        }
    }
}
