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

        virtual std::vector<ICamera::Capabilities> GetCapabilities() const override;
        virtual void SetFormat(const ICamera::Capabilities& cap) override;
        virtual void TakeAndSavePicture() const override;
    
    private:
        FrameEncoding PixelFormatToFrameEncoding(unsigned int pixelFormat) const;
        unsigned int FrameEncodingToPixelFormat(FrameEncoding encoding) const;

        void StartStreaming();
        void StopStreaming();

    private:
        int m_fd;
        MMapBuffers* m_buffers;
    };

}

#endif // __linux__
