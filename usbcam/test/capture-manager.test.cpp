#include <catch2/catch.hpp>
#include "capture-manager.h"

#include <iostream>

SCENARIO("A Capture Manager can handle multiple camera, change settings, launch capture and save images in multithread", "[capture-manager]") {
    /*
    GIVEN("Multiple plugged devices") {
        WHEN("I ask for the connected cameras") {
            const auto list = USBCam::GetDevicesList();

            THEN("I should get a list of names and port numbers") {
                REQUIRE(list.size() > 0);
            }
        }
    }
    */

    GIVEN("A single Camera") {
        USBCam::CaptureManager manager({0});

        WHEN("I ask for its capabilities") {
            auto caps = manager.GetCam(0)->GetCapabilities();

            THEN("I should get them") {
                std::cout << caps.at(0).frameRate;
            }
        }

        /*
        WHEN("I take a picture") {
            manager.GetCam(0)->TakeAndSavePicture();

            THEN("It should save it") {
                REQUIRE(true);
            }
        }
        */
    }

    /*

    GIVEN("3 Cameras") {
        USBCam::CaptureManager manager({0, 2, 3});

        WHEN("I take a picture with each cameras") {
            manager.TakeAndSavePictures();

            THEN("It should work") {
                REQUIRE(true);
            }
        }
    }
    */
}
