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
            AUTO_WHITE_BALANCE,
            AUTO_EXPOSURE,
            AUTO_ISO,
            BRIGHTNESS,
            CONTRAST,
            EXPOSURE,
            ENABLE_HDR,
            ENABLE_STABILIZATION,
            GAMMA,
            HUE,
            ISO,
            SATURATION,
            SHARPNESS,
            WHITE_BALANCE
        };

        /**
         * @brief Camera settings with possible values
         */
        struct CameraSettingDetail {
            CameraSetting type = CameraSetting::_UNKNOWN;
            int32_t min = 0;
            int32_t max = 10000;
        };

        /**
         * @brief Camera frame data structure
         */
        struct Frame {
            Format format;
            unsigned int byteWidth = 0;
            std::vector<unsigned char> data;
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
         * @brief Store a value for the format. Not applied to the camera
         * 
         * @param cap - Camera capability
         */
        void SetUnappliedFormat(const Format& cap) {
            m_unappliedFormat = cap;
        }

        /**
         * @brief Get the Unapplied stored format
         * 
         * @return Format
         */
        Format GetUnappliedFormat() {
            return m_unappliedFormat;
        }

        /**
         * @brief Get the Format used by the camera
         * 
         * @return Format 
         */
        virtual Format GetFormat() const = 0;

        /**
         * @brief Get the Supported Settings of the camera
         * 
         * @return std::vector<CameraSettingDetail> 
         */
        virtual std::vector<CameraSettingDetail> GetSupportedSettings() const = 0;

        /**
         * @brief Set the Camera setting
         * 
         * @param setting 
         * @param value 
         * @return bool - True on success, False on error
         */
        virtual bool SetSetting(CameraSetting setting, int value) = 0;

        /**
         * @brief Get the setting value
         * 
         * @param setting 
         * @return int 
         */
        virtual int GetSetting(CameraSetting setting) const = 0;

        /**
         * @brief Set the Save Directory for output images
         * 
         * @param path 
         */
        virtual void SetSaveDirectory(const std::string& path) = 0;

        /**
         * @brief Take a picture and save it the save directory
         */
        virtual void SaveLastFrame() = 0;

        /**
         * @brief Take a picture and give a const reference to its data
         * 
         * @return Frame&
         */
        virtual const Frame& GetLastFrame() = 0;

        /**
         * @brief Translates Camera Setting enum to string
         * 
         * @param setting 
         * @return std::string 
         */
        static std::string CameraSettingToString(CameraSetting setting) {
            switch (setting) {
            case CameraSetting::BRIGHTNESS: return "Brightness";
            case CameraSetting::CONTRAST: return "Constrast";
            case CameraSetting::SATURATION: return "Saturation";
            case CameraSetting::GAMMA: return "Gamma";
            case CameraSetting::HUE: return "Hue";
            case CameraSetting::WHITE_BALANCE: return "White balance";
            case CameraSetting::AUTO_WHITE_BALANCE: return "Auto white balance";
            case CameraSetting::AUTO_EXPOSURE: return "Auto exposure";
            case CameraSetting::AUTO_ISO: return "Auto iso";
            case CameraSetting::ISO: return "Iso";
            case CameraSetting::SHARPNESS: return "Sharpness";
            case CameraSetting::EXPOSURE: return "Exposure";
            case CameraSetting::ENABLE_HDR: return "Enable High Dynamic Range";
            case CameraSetting::ENABLE_STABILIZATION: return "Enable optic stabilization";
            default: return "Unknown";
            }
        }

        private:
            Format m_unappliedFormat;
    };
}
