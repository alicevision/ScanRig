#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "capture-manager.h"
#include "i-camera.h"

namespace py = pybind11;

namespace USBCam {

    PYBIND11_MODULE(usbcam, m) {
        m.def("GetDevicesList", &GetDevicesList, "Get connected devices");

        py::class_<Port>(m, "Port")
            .def_readonly("number", &Port::number)
            .def_readonly("name", &Port::name);

        py::class_<ICamera::Capabilities>(m, "Capabilities")
            .def_readonly("id", &ICamera::Capabilities::id)
            .def_readonly("frameRate", &ICamera::Capabilities::frameRate)
            .def_readonly("width", &ICamera::Capabilities::width)
            .def_readonly("height", &ICamera::Capabilities::height)
            .def_readonly("encoding", &ICamera::Capabilities::encoding);

        py::class_<ICamera>(m, "ICamera")
            .def("GetCapabilities", &ICamera::GetCapabilities)
            .def("SetFormat", &ICamera::SetFormat);

        py::class_<CaptureManager>(m, "CaptureManager")
            .def(py::init<std::vector<uint32_t>>())
            .def("GetCam", &CaptureManager::GetCam)
            .def("TakeAndSavePictures", &CaptureManager::TakeAndSavePictures);
    }
}
