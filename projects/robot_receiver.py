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
PIVOT_SPEED = 40000  # Adjusted for 16-bit scaling
DECELERATION_RATE = 5000  # Speed decrement per step for controlled stopping.
DECELERATION_DELAY = 0.02  # Delay between deceleration steps.

# State variables.
last_enable_state = None
last_motor_direction = None
brake_engaged = False

# Define a deadzone threshold.
THRESHOLD = 10

def gradual_stop():
    """Gradually stops the motors without engaging brakes."""
    global current_speed
    if current_speed == 0:
        return
    debug_print(1, "Initiating gradual stop.")
    while current_speed > 0:
        current_speed = max(0, current_speed - DECELERATION_RATE)
        motor.set_speed(current_speed, current_speed)
        time.sleep(DECELERATION_DELAY)
    motor.set_speed(0, 0)
    debug_print(1, "Motors set to speed 0, no brakes engaged.")

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
                motor.apply_brakes()
                brake_engaged = True
            continue
        else:
            if brake_engaged:
                motor.release_brakes()
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

        if abs(joystick_y - 128) > THRESHOLD:
            fraction = abs(joystick_y - 128) / 127.0
            speed_value = int(fraction * 65535)  # Scale to full PWM range
            if joystick_y > 128:
                motor.move_forward(speed_value)
                debug_print(1, "Moving forward at speed", speed_value)
                last_motor_direction = "forward"
            else:
                motor.move_reverse(speed_value)
                debug_print(1, "Moving reverse at speed", speed_value)
                last_motor_direction = "reverse"
            current_speed = speed_value
        elif abs(joystick_x - 128) > THRESHOLD:
            if joystick_x < 128:
                motor.pivot_left(PIVOT_SPEED)
                debug_print(1, "Pivoting left.")
                last_motor_direction = "pivot_left"
            elif joystick_x > 128:
                motor.pivot_right(PIVOT_SPEED)
                debug_print(1, "Pivoting right.")
                last_motor_direction = "pivot_right"
        else:
            gradual_stop()
            last_motor_direction = "stopped"

    except Exception as e:
        print("Error processing received message:", e)

    time.sleep(0.02)
