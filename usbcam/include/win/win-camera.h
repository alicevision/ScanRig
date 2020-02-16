#pragma once

#ifdef _WIN32

#include "camera.h"

#include <vector>
#include <string>
#include <stdint.h>

#include <Windows.h>
#include <conio.h>
#include <Mferror.h>
#include <winrt\base.h>
#include <winrt\Windows.Foundation.h>
#include <winrt\Windows.Foundation.Collections.h>
#include <winrt\Windows.Media.Capture.h>
#include <winrt\Windows.Media.Core.h>
#include <winrt\Windows.Media.Devices.h>
#include <winrt\Windows.Media.MediaProperties.h>
#include <winrt\Windows.Media.Capture.Frames.h>
#include <winrt\Windows.Devices.Enumeration.h>
#include <winrt\Windows.Graphics.Imaging.h>
#include <winrt\Windows.Storage.h>
#include <winrt\Windows.Storage.Streams.h>

using namespace winrt;
using namespace Windows::Media::Capture;
using namespace Windows::Media::MediaProperties;
using namespace Windows::Media::Capture::Frames;
using namespace Windows::Foundation;
using namespace Windows::Foundation::Collections;
using namespace Windows::Devices::Enumeration;
using namespace Windows::Storage;
using namespace Windows::Graphics::Imaging;
using namespace Windows::Media::Core;

namespace USBCam {

    class WinCamera : public Camera {
    public:
        WinCamera(uint32_t portNumber);
        virtual ~WinCamera();

        virtual std::vector<Camera::Capabilities> GetCapabilities() const override;
    };
}

#endif // _WIN32
