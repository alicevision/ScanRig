#include <pybind11/pybind11.h>

#include "capture-manager.h"

namespace py = pybind11;

namespace USBCam {

    PYBIND11_MODULE(usbcam, m) {
        m.def("GetDevicesList", &GetDevicesList, "Get connected devices");
    }

/*
    PYBIND11_MODULE(CaptureManager, m) {
    py::class_<CaptureManager>(m, "CaptureManager")
        .def(py::init<std::vector<uint32_t>>())
        .def("GetCam", &CaptureManager::GetCam)
        .def("TakeAndSavePictures", &CaptureManager::TakeAndSavePictures);
    }
*/
}
