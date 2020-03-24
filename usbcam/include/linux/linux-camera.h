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

        virtual std::vector<Capabilities> GetCapabilities() const override;
        virtual void SetFormat(const Capabilities& cap) override;
        virtual Capabilities GetFormat() override;
        
        virtual void SetSetting(CameraSetting setting, unsigned int value) override;
        virtual unsigned int GetSetting(CameraSetting setting) override;

        // Control methods

        virtual void TakeAndSavePicture() override;
    
    private:
        FrameEncoding PixelFormatToFrameEncoding(unsigned int pixelFormat) const;
        unsigned int FrameEncodingToPixelFormat(FrameEncoding encoding) const;
        CameraSetting ControlIdToCameraSetting(unsigned int controlId) const;
        unsigned int CameraSettingToControlId(CameraSetting setting) const;

        void StartStreaming();
        void StopStreaming();

        /**
         * @brief Wait for a buffer to be available
         */
        void Wait() const;

    private:
        int m_fd;
        unsigned int m_id;
        unsigned int m_frameCount;
        MMapBuffers* m_buffers;
    };

}

#endif // __linux__
