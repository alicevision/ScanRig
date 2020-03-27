#include <catch2/catch.hpp>
#include "device-handling.h"

#include <iostream>

SCENARIO("We should be able to create and control cameras connected by USB", "[camera]") {
    GIVEN("One plugged camera") {
        WHEN("I ask for the connected cameras") {
            const auto list = USBCam::GetDevicesList();

            THEN("I should get a list of names and port numbers") {
                REQUIRE(list.size() > 0);
                REQUIRE(list.at(0).name != "");
            }
        }

        WHEN("I want to take control of a camera") {
            auto camera0 = USBCam::CreateCamera(1);

            THEN("I should be able to take a picture") {
                REQUIRE_NOTHROW(camera0->SaveLastFrame());
            }
            THEN("I should be able to change its settings") {
                REQUIRE(camera0->SetSetting(USBCam::ICamera::CameraSetting::BRIGHTNESS, 0));
                REQUIRE_NOTHROW(camera0->SaveLastFrame());
                REQUIRE(camera0->SetSetting(USBCam::ICamera::CameraSetting::BRIGHTNESS, 10000));
                REQUIRE_NOTHROW(camera0->SaveLastFrame());
            }
        }
    }
}
