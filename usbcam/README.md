# Python USB Camera

Small C++ library to control USB Cameras. It has a python binding.

If you want to use a DSLR, have a look at [GPhoto2](http://www.gphoto.org/) and its python binding.

## Supported OS

| Name | Status | Underlying API |
| --- | --- | --- |
| Windows 10 | In progress | [Windows UWP CameraCapture](https://docs.microsoft.com/en-us/uwp/api/windows.media.capture.mediacapture) |
| Linux | In progresss | [V4l2](https://linuxtv.org/downloads/v4l-dvb-apis/uapi/v4l/v4l2.html) |
| MacOS | No | |

## Getting Started

### Install as python extension

`pip install .`

### Build in C++

TODO

### Run test

TODO

## Documentation

### Linux

| Link | Description |
| --- | --- |
| [v4l2 introduction](https://lwn.net/Articles/203924/) | |
| [Capture Webcam stream with using v4l2](http://jwhsmith.net/2014/12/capturing-a-webcam-stream-using-v4l2/) | |
| [Chromium source v4l2 implementation](https://chromium.googlesource.com/chromium/src.git/+/40.0.2214.91/media/video/capture/linux/video_capture_device_linux.cc) | |
| [OpenCV v4l2 implementation](https://github.com/opencv/opencv/blob/master/modules/videoio/src/cap_v4l.cpp) | |
| [v4l2 API Documentation](https://linuxtv.org/downloads/v4l-dvb-apis-new/uapi/v4l/v4l2.html) | |
| [v4l2 official example](https://linuxtv.org/downloads/v4l-dvb-apis/uapi/v4l/capture.c.html) | |

### Windows

| Link | Description |
| --- | --- |
| [Windows Universal Camera samples](https://github.com/microsoft/Windows-universal-samples/tree/master/Samples/CameraStarterKit) | |

