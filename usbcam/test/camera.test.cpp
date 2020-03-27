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

    GIVEN("A plugged camera") {
        auto camera0 = USBCam::CreateCamera(0);

        WHEN("I change its settings") {
            REQUIRE(camera0->SetSetting(USBCam::ICamera::CameraSetting::BRIGHTNESS, 10));

            THEN("The settings should be changed") {
                REQUIRE(camera0->GetSetting(USBCam::ICamera::CameraSetting::BRIGHTNESS) == 10);
            }
        }
    }
}
