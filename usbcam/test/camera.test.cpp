#include <catch2/catch.hpp>
#include "device-handling.h"

#include <iostream>

SCENARIO("We should be able to create and control cameras connected by USB", "[camera]") {
    GIVEN("Multiple plugged devices") {
        WHEN("I ask for the connected cameras") {
            const auto list = USBCam::GetDevicesList();

            THEN("I should get a list of names and port numbers") {
                REQUIRE(list.size() > 0);
                REQUIRE(list.at(0).name != "");
            }
        }
    }
}
