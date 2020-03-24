#pragma once

#include <vector>
#include <string>
#include <stdint.h>

namespace USBCam {
    /**
     * @brief Abstract Interface to control a USB Camera under any OS.
     */
    class ICamera {
    public:
        /**
         * @brief Data format supported by the camera
         */
        enum class FrameEncoding {
            _UNKNOWN,
            YUY2,
            UYVY,
            MJPG,
            NV12
        };

        /**
         * @brief Capture settings supported by the camera
         */
        struct Format {
            uint32_t id = 0;
            uint32_t frameRate = 0;
            uint32_t width = 0;
            uint32_t height = 0;
            FrameEncoding encoding = FrameEncoding::_UNKNOWN;
        };

        /**
         * @brief Camera settings that can be set by the user
         */
        enum class CameraSetting {
            _UNKNOWN,
            BRIGHTNESS,
            CONTRAST,
            SATURATION,
            GAMMA,
            HUE,
            WHITE_BALANCE,
            AUTO_WHITE_BALANCE,
            GAIN,
            SHARPNESS,
            EXPOSURE
        };

        virtual ~ICamera() {};

        /**
         * @brief Get the record values supported by the camera
         * @return std::vector<Format> 
         */
        virtual std::vector<Format> GetSupportedFormats() const = 0;

        /**
         * @brief Set the capture setting of the camera
         * 
         * @param cap - Camera capability
         */
        virtual void SetFormat(const Format& cap) = 0;

        /**
         * @brief Get the Format used by the camera
         * 
         * @return Format 
         */
        virtual Format GetFormat() = 0;

        /**
         * @brief Get the Supported Settings of the camera
         * 
         * @return std::vector<CameraSetting> 
         */
        virtual std::vector<CameraSetting> GetSupportedSettings() const = 0;

        /**
         * @brief Set the Camera setting
         * 
         * @param setting 
         * @param value 
         */
        virtual void SetSetting(CameraSetting setting, int value) = 0;

        /**
         * @brief Get the setting value
         * 
         * @param setting 
         * @return unsigned int 
         */
        virtual unsigned int GetSetting(CameraSetting setting) = 0;

        /**
         * @brief Take a picture and save it in current working directory
         */
        virtual void TakeAndSavePicture() = 0;

        static std::string CameraSettingToString(CameraSetting setting) {
            switch (setting) {
            case CameraSetting::BRIGHTNESS: return "Brightness";
            case CameraSetting::CONTRAST: return "Constrast";
            case CameraSetting::SATURATION: return "Saturation";
            case CameraSetting::GAMMA: return "Gamma";
            case CameraSetting::HUE: return "Hue";
            case CameraSetting::WHITE_BALANCE: return "White balance";
            case CameraSetting::AUTO_WHITE_BALANCE: return "Auto white balance";
            case CameraSetting::GAIN: return "Gain";
            case CameraSetting::SHARPNESS: return "Sharpness";
            case CameraSetting::EXPOSURE: return "Exposure";
            default: return "Unknown";
            }
        }
    };
}
