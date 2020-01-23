#include <stdio.h>
#include <opencv2/highgui/highgui_c.h>
#include <chrono>
#include <thread>
#include <iostream>

#include "libuvc/libuvc.h"

void cb(uvc_frame_t *frame, void *ptr) {
    uvc_frame_t *bgr;
    uvc_error_t ret;
    IplImage *cvImg;

    std::cout << "callback! length = " << frame->data_bytes << std::endl;

    /*
    bgr = uvc_allocate_frame(frame->width * frame->height * 3);
    if (!bgr)
    {
        printf("unable to allocate bgr frame!");
        return;
    }

    // FIXME segfault with this function with 4208x3120 resolution
    ret = uvc_any2bgr(frame, bgr);
    if (ret)
    {
        uvc_perror(ret, "uvc_any2bgr");
        uvc_free_frame(bgr);
        return;
    }

    cvImg = cvCreateImageHeader(
        cvSize(bgr->width, bgr->height),
        IPL_DEPTH_8U,
        3);

    cvSetData(cvImg, bgr->data, bgr->width * 3);

    cvNamedWindow("Test", CV_WINDOW_AUTOSIZE);
    cvShowImage("Test", cvImg);
    cvWaitKey(10);

    cvReleaseImageHeader(&cvImg);

    uvc_free_frame(bgr);
    */
}

int main(int argc, char **argv) {
    const int deviceId = 0;
    uvc_error_t res;

    uvc_context_t *ctx;
    res = uvc_init(&ctx, NULL);
    if (res < 0) {
        uvc_perror(res, "uvc_init");
        return res;
    }

    puts("UVC initialized");
    uvc_device_t **devices;
    res = uvc_find_devices(ctx, &devices, 0, 0, NULL);
    if (res < 0) {
        uvc_perror(res, "uvc_find_device");
        return res;
    }

    puts("Device found");
    uvc_device_handle_t *devh;
    res = uvc_open(devices[deviceId], &devh);
    if (res < 0) {
        uvc_perror(res, "uvc_open");
        return res;
    }

    puts("Device opened");
    uvc_print_diag(devh, stderr);

    uvc_stream_ctrl_t ctrl;
    res = uvc_get_stream_ctrl_format_size( devh, &ctrl, UVC_FRAME_FORMAT_UYVY, 4208, 3120, 9);
    uvc_print_stream_ctrl(&ctrl, stderr);
    if (res < 0) {
        uvc_perror(res, "get_mode");
        return res;
    }

    res = uvc_start_streaming(devh, &ctrl, cb, (void*) 12345, 0);
    std::this_thread::sleep_for(std::chrono::milliseconds(10000));
    uvc_stop_streaming(devh);
    puts("Done streaming.");

    uvc_close(devh);
    puts("Device closed");
    uvc_unref_device(devices[deviceId]);
    uvc_exit(ctx);
    puts("UVC exited");

    return 0;
}
