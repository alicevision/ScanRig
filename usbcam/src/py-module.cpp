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

        py::class_<ICamera::Format>(m, "Format")
            .def_readonly("id", &ICamera::Format::id)
            .def_readonly("frameRate", &ICamera::Format::frameRate)
            .def_readonly("width", &ICamera::Format::width)
            .def_readonly("height", &ICamera::Format::height)
            .def_readonly("encoding", &ICamera::Format::encoding);

        py::class_<ICamera>(m, "ICamera")
            .def("GetSupportedFormats", &ICamera::GetSupportedFormats)
            .def("SetFormat", &ICamera::SetFormat);
    }
}
