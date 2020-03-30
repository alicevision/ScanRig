#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "device-handling.h"
#include "i-camera.h"

namespace py = pybind11;

namespace USBCam {

    PYBIND11_MODULE(usbcam, m) {
        m.def("GetDevicesList", &GetDevicesList, "Get connected devices");
        m.def("CreateCamera", &CreateCamera, "Create a new camera");

        py::class_<Port>(m, "Port")
            .def_readonly("number", &Port::number)
            .def_readonly("name", &Port::name);

        py::enum_<ICamera::FrameEncoding>(m, "FrameEncoding")
            .value("_Unknown", ICamera::FrameEncoding::_UNKNOWN)
            .value("YUY2", ICamera::FrameEncoding::YUY2)
            .value("UYVY", ICamera::FrameEncoding::UYVY)
            .value("MJPG", ICamera::FrameEncoding::MJPG)
            .value("NV12", ICamera::FrameEncoding::NV12);

        py::class_<ICamera::Format>(m, "Format")
            .def_readonly("id", &ICamera::Format::id)
            .def_readonly("frameRate", &ICamera::Format::frameRate)
            .def_readonly("width", &ICamera::Format::width)
            .def_readonly("height", &ICamera::Format::height)
            .def_readonly("encoding", &ICamera::Format::encoding);

        py::enum_<ICamera::CameraSetting>(m, "CameraSetting")
            .value("_Unknown", ICamera::CameraSetting::_UNKNOWN)
            .value("Auto_Exposure", ICamera::CameraSetting::AUTO_EXPOSURE)
            .value("Auto_Iso", ICamera::CameraSetting::AUTO_ISO)
            .value("Auto_White_Balance", ICamera::CameraSetting::AUTO_WHITE_BALANCE)
            .value("Brightness", ICamera::CameraSetting::BRIGHTNESS)
            .value("Contrast", ICamera::CameraSetting::CONTRAST)
            .value("Exposure", ICamera::CameraSetting::EXPOSURE)
            .value("Enable_HDR", ICamera::CameraSetting::ENABLE_HDR)
            .value("Enable_Stabilization", ICamera::CameraSetting::ENABLE_STABILIZATION)
            .value("Gamma", ICamera::CameraSetting::GAMMA)
            .value("Hue", ICamera::CameraSetting::HUE)
            .value("Iso", ICamera::CameraSetting::ISO)
            .value("Saturation", ICamera::CameraSetting::SATURATION)
            .value("Sharpness", ICamera::CameraSetting::SHARPNESS)
            .value("White_Balance", ICamera::CameraSetting::WHITE_BALANCE);

        py::class_<ICamera::CameraSettingDetail>(m, "CameraSettingDetail")
            .def_readonly("type", &ICamera::CameraSettingDetail::type)
            .def_readonly("min", &ICamera::CameraSettingDetail::min)
            .def_readonly("max", &ICamera::CameraSettingDetail::max);

        py::class_<ICamera::Frame>(m, "Frame", py::buffer_protocol())
            .def_readonly("byteWidth", &ICamera::Frame::byteWidth)
            .def_readonly("format", &ICamera::Frame::format)
            .def_buffer([](ICamera::Frame& im) -> py::buffer_info {
                py::buffer_info info;
                info.ptr =  im.data.data();
                info.size = im.byteWidth;
                info.itemsize = sizeof(unsigned char);
                info.format = py::format_descriptor<unsigned char>::format();
                info.ndim = 1;
                info.readonly = true;
                info.shape = { im.byteWidth };
                info.strides = { sizeof(unsigned char) };
                return info;
            });

        py::class_<ICamera>(m, "ICamera")
            .def("GetSupportedFormats", &ICamera::GetSupportedFormats)
            .def("SetFormat", &ICamera::SetFormat)
            .def("GetFormat", &ICamera::GetFormat)
            .def("GetSupportedSettings", &ICamera::GetSupportedSettings)
            .def("SetSetting", &ICamera::SetSetting)
            .def("GetSetting", &ICamera::GetSetting)
            .def("SetSaveDirectory", &ICamera::SetSaveDirectory)
            .def("SaveLastFrame", &ICamera::SaveLastFrame)
            .def("GetLastFrame", &ICamera::GetLastFrame)
            .def("CameraSettingToString", &ICamera::CameraSettingToString);
    }
}
