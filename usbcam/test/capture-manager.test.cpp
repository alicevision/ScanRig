#include <catch2/catch.hpp>
#include "capture-manager.h"

#include <iostream>

SCENARIO("A Capture Manager can handle multiple camera, change settings, launch capture and save images in multithread", "[capture-manager]") {
    GIVEN("Multiple plugged devices") {
        WHEN("I ask for the connected cameras") {
            const auto list = USBCam::GetDevicesList();

            THEN("I should get a list of names and port numbers") {
                REQUIRE(list.size() > 0);
            }
        }
    }
}
