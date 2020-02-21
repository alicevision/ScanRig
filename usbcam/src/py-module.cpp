#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "capture-manager.h"

namespace py = pybind11;

namespace USBCam {

    PYBIND11_MODULE(usbcam, m) {
        m.def("GetDevicesList", &GetDevicesList, "Get connected devices");

        py::class_<Port>(m, "Port")
            .def_readonly("number", &Port::number)
            .def_readonly("name", &Port::name);

        py::class_<CaptureManager>(m, "CaptureManager")
            .def(py::init<std::vector<uint32_t>>())
            .def("GetCam", &CaptureManager::GetCam)
            .def("TakeAndSavePictures", &CaptureManager::TakeAndSavePictures);
    }
}
