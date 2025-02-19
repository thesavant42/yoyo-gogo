"""
Test Wheel Script
-----------------
This script allows testing individual wheels by utilizing the test_wheel function
from the circuitpython_zsx11h motor control library.

Usage:
- Set the wheel to "left" or "right".
- Set a speed value (0-255).
- Observe the behavior to determine if direction configuration needs adjustment.
"""

import time
import circuitpython_zsx11h as motor

# ---- User Configuration ----
WHEEL_TO_TEST = "left"  # Change to "right" to test the right wheel
TEST_SPEED = 100  # Adjust speed as needed (0-255)
TEST_DURATION = 3  # Number of seconds to run the test

print(f"Testing {WHEEL_TO_TEST} wheel at speed {TEST_SPEED} for {TEST_DURATION} seconds...")

# Run the wheel test
motor.test_wheel(WHEEL_TO_TEST, TEST_SPEED)

time.sleep(TEST_DURATION)  # Allow test to run

# Stop the motor after the test duration
motor.stop()
print(f"{WHEEL_TO_TEST.capitalize()} wheel test complete.")