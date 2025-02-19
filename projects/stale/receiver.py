"""
Updated code.py
-----------------
This script runs on an Adafruit ESP32-S3 Feather (MAC: 70:04:1D:CD:F8:70).
It receives ESP-NOW messages, decodes control data from a CSV string, and maps
joystick/button inputs to motor commands using the circuitpython_zsx11h motor control library.
"""

import time
import wifi
import espnow
import circuitpython_zsx11h as motor

# ---- Configurable Debug Verbosity ----
# DEBUG_LEVEL: 0 = no debug output, 1 = minimal output, 2 = verbose output.
DEBUG_LEVEL = 0

def debug_print(level, *args):
    if DEBUG_LEVEL >= level:
        print(" ".join(str(arg) for arg in args))

wifi.radio.enabled = False

def mac_to_bytes(mac_str):
    """
    Convert a MAC address string to bytes.
    """
    return bytes(int(b, 16) for b in mac_str.split(":"))

expected_sender_mac = mac_to_bytes("F4:12:FA:5A:51:48")

try:
    esp = espnow.ESPNow()
except Exception as e:
    debug_print(1, "Failed to initialize ESP-NOW:", e)
    raise

current_speed = 0
PIVOT_SPEED = 150
THRESHOLD = 10
MAX_FRACTION = 0.6 # 0.2

debug_print(1, "Receiver is ready and listening for ESP-NOW messages...")

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

            x = int(parts[0])
            y = int(parts[1])
            c = bool(int(parts[2]))
            z = bool(int(parts[3]))
            control_data = {"x": x, "y": y, "c": c, "z": z}
            debug_print(2, "DEBUG: Parsed control data:", control_data)

        except Exception as e:
            debug_print(1, "DEBUG: Failed to parse message:", e)
            continue

        # Ensure C button is checked first
        c_pressed = control_data.get("c", False)
        debug_print(1, "Button C state:", c_pressed)
        motor.handle_c_button(c_pressed)

        # Determine motor enable state from button Z.
        enable_state = control_data.get("z", False)
        if enable_state:
            motor.enable_motors(True)
        else:
            motor.enable_motors(False)
            motor.stop()
            continue

        joystick_x = control_data.get("x", 128)
        joystick_y = control_data.get("y", 128)

        if abs(joystick_y - 128) > THRESHOLD:
            fraction = (abs(joystick_y - 128) / 127.0) * MAX_FRACTION
            speed_value = int(fraction * 255)
            if joystick_y > 128:
                motor.move_forward(speed_value)
                debug_print(1, "Moving forward at speed:", speed_value)
            else:
                motor.move_reverse(speed_value)
                debug_print(1, "Moving reverse at speed:", speed_value)

        elif abs(joystick_x - 128) > THRESHOLD:
            if joystick_x < 128:
                motor.pivot_left(PIVOT_SPEED)
                debug_print(1, "Pivoting left.")
            elif joystick_x > 128:
                motor.pivot_right(PIVOT_SPEED)
                debug_print(1, "Pivoting right.")
        else:
            motor.stop()
            debug_print(1, "Stopping motors.")

    except Exception as e:
        debug_print(1, "Error processing received message:", e)

    time.sleep(0.02)
