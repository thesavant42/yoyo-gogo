"""
robot-receiver.py
-----------------
This script runs on an Adafruit ESP32-S3 Feather (MAC: 70:04:1D:CD:F8:70).
It receives ESP-NOW messages, decodes control data from a CSV string, and maps
joystick/button inputs to motor commands using the circuitpython_zsx11h motor control library.

Control Logic:
  - Joystick Y (vertical):
      If moved significantly away from neutral (128):
          Y > 128 -> forward
          Y < 128 -> reverse
      Scaling: The fraction = (|Y - 128| / (127 or 128)) * MAX_FRACTION,
      and speed_value = int(fraction * 255).
  - Joystick X (horizontal):
      If Y is near neutral (within THRESHOLD), then use X:
          X < 128 -> pivot left
          X > 128 -> pivot right
  - Button C (Brake): Gradually stops the motors while held.
  - Button Z (Gas): While TRUE, motors remain enabled.
    When FALSE, the motors are disabled and stopped.

Important: The sender must send the control data as a CSV string encoded via .encode("utf-8").
Example: "128,128,0,1"
"""

import time
import wifi
import espnow
import circuitpython_zsx11h as motor

# ---- Configurable Debug Verbosity ----
DEBUG_LEVEL = 1

def debug_print(level, *args):
    if DEBUG_LEVEL >= level:
        print(" ".join(str(arg) for arg in args))

# Disable Wi-Fi to ensure ESP-NOW works properly.
wifi.radio.enabled = False

def mac_to_bytes(mac_str):
    return bytes([int(b, 16) for b in mac_str.split(":" )])

expected_sender_mac = mac_to_bytes("F4:12:FA:5A:51:48")

try:
    esp = espnow.ESPNow()
except Exception as e:
    print("Failed to initialize ESP-NOW:", e)
    raise

# Motor control variables.
current_speed = 0
PIVOT_SPEED = 150  # Use fixed pivot speed.
DECELERATION_RATE = 50  # Speed decrement per step for controlled stopping.
DECELERATION_DELAY = 0.02  # Delay between deceleration steps.

# State variables.
last_enable_state = None
last_motor_direction = None
brake_engaged = False

# Variables to limit repeated error messages.
last_invalid_error_time = 0
ERROR_PRINT_INTERVAL = 5  # seconds

# Define a deadzone threshold.
THRESHOLD = 10

# Scaling constant: maximum fraction of full speed to use.
MAX_FRACTION = 0.2

def clamp(value, min_value, max_value):
    """Ensures a value stays within a valid range."""
    return max(min_value, min(value, max_value))

def gradual_stop():
    """Gradually stops the motors to prevent sudden halts that may damage hardware."""
    global current_speed
    if current_speed == 0:
        return  # Avoid unnecessary calls
    debug_print(1, "Initiating gradual stop.")
    while current_speed > 0:
        current_speed = clamp(current_speed - DECELERATION_RATE, 0, 255)
        motor.set_speed(current_speed, current_speed)
        time.sleep(DECELERATION_DELAY)
    motor.stop()
    debug_print(1, "Motors stopped with braking engaged.")

print("Receiver is ready and listening for ESP-NOW messages...")

while True:
    try:
        packet = esp.read()
        if not packet:
            time.sleep(0.1)
            continue

        sender_mac_str = ":".join("{:02X}".format(b) for b in packet.mac)
        debug_print(2, "DEBUG: Packet received from MAC:", sender_mac_str)
        if packet.mac != expected_sender_mac:
            continue

        try:
            data_str = packet.msg.decode("utf-8").strip()
            if not data_str:
                continue

            parts = data_str.split(',')
            if len(parts) != 4:
                continue

            x, y, c, z = map(int, parts)
            control_data = {"x": x, "y": y, "c": bool(c), "z": bool(z)}
        except Exception:
            continue

        enable_state = control_data.get("z", False)
        brake_pressed = control_data.get("c", False)

        if brake_pressed:
            if not brake_engaged:
                debug_print(1, "Brake engaged by C button.")
                gradual_stop()
                motor.enable_motors(False)
                brake_engaged = True
            continue
        else:
            if brake_engaged:
                motor.enable_motors(True)
                debug_print(1, "Brakes released, motors re-enabled.")
                brake_engaged = False

        if enable_state != last_enable_state:
            motor.enable_motors(enable_state)
            last_enable_state = enable_state

        if not enable_state:
            if last_motor_direction != "stopped":
                gradual_stop()
                last_motor_direction = "stopped"
            continue

        joystick_x = control_data.get("x", 128)
        joystick_y = control_data.get("y", 128)

        if abs(joystick_x - 128) <= THRESHOLD and abs(joystick_y - 128) <= THRESHOLD:
            motor.neutral_speed()
            last_motor_direction = "stopped"
            continue
            motor.neutral_speed()
            last_motor_direction = "stopped"
            continue

    except Exception as e:
        print("Error processing received message:", e)

    time.sleep(0.02)
