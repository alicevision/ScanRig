#pragma once

#ifdef __linux__

#include "i-camera.h"

#include <vector>
#include <string>
#include <stdint.h>

#include "mmap-buffers.h"

namespace USBCam {
    class LinuxCamera : public ICamera {
    public:
        LinuxCamera(uint32_t portNumber);
        virtual ~LinuxCamera();

        // Getters and setters

        virtual std::vector<Format> GetSupportedFormats() const override;
        virtual void SetFormat(const Format& cap) override;
        virtual Format GetFormat() const override;
        
        virtual std::vector<CameraSettingDetail> GetSupportedSettings() const override;
        virtual bool SetSetting(CameraSetting setting, int value) override;
        virtual int GetSetting(CameraSetting setting) const override;

        // Control methods

        virtual void SetSaveDirectory(std::string path) override;
        virtual void SaveLastFrame() override;
        virtual const Frame& GetLastFrame() override;
    
    private:
        FrameEncoding PixelFormatToFrameEncoding(unsigned int pixelFormat) const;
        unsigned int FrameEncodingToPixelFormat(FrameEncoding encoding) const;

        /**
         * @link https://www.kernel.org/doc/html/v4.14/media/uapi/v4l/control.html
         */
        CameraSetting ControlIdToCameraSetting(unsigned int controlId) const;
        unsigned int CameraSettingToControlId(CameraSetting setting) const;

        void StartStreaming();
        void StopStreaming();
        void CreateCaptureFolders();
        void QueryControlMenuItems(unsigned int controlId, int min, int max) const;

        /**
         * @brief Wait for a buffer to be available
         */
        void Wait() const;

    private:
        int m_fd;
        unsigned int m_id;
        unsigned int m_frameCount;
        MMapBuffers* m_buffers;
        Frame m_frame;
        std::string m_savePath;
    };

}

#endif // __linux__
