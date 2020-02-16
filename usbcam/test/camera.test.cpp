#include <catch2/catch.hpp>
#include "camera.h"

#include <iostream>

SCENARIO("A Camera can be detected, opened, we can change its settings and grab a frame", "[camera]") {
    GIVEN("Multiple plugged devices") {
        WHEN("I ask for the connected cameras") {

            THEN("I should get a list of names and port numbers") {
                REQUIRE(true);
            }
        }
    }
}
