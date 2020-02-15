#include <catch2/catch.hpp>
#include "camera.h"

SCENARIO("Casting operation allows to retrieve the same value accross different type", "[camera]") {
    GIVEN("An unsigned int value") {
        int myVal = 1;

        WHEN("I cast its bits into a float") {
            // TODO

            THEN("I should retrieve it when I cast back") {
                // TODO

                REQUIRE(true);
            }
        }
    }
}
