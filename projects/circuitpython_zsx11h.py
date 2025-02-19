import time
import pwmio
import digitalio
import board

# Constants
MAX_SPEED = 65535  # Updated max speed for full 16-bit scaling
RAMP_STEPS = 10  # Number of steps for speed ramping
RAMP_DELAY = 0.02  # Delay between ramping steps

# Initialize motor PWM outputs
left_pwm = pwmio.PWMOut(board.A0, frequency=2000, duty_cycle=0)
right_pwm = pwmio.PWMOut(board.D9, frequency=2000, duty_cycle=0)

# Initialize direction control pins
left_dir = digitalio.DigitalInOut(board.A1)
left_dir.direction = digitalio.Direction.OUTPUT
right_dir = digitalio.DigitalInOut(board.D12)
right_dir.direction = digitalio.Direction.OUTPUT

# Initialize brake pins
left_brake = digitalio.DigitalInOut(board.A2)
left_brake.direction = digitalio.Direction.OUTPUT
right_brake = digitalio.DigitalInOut(board.D11)
right_brake.direction = digitalio.Direction.OUTPUT

motors_enabled = True  # Global motor state

def clamp(value, min_value, max_value):
    """Ensures a value stays within a valid range."""
    return max(min_value, min(value, max_value))

def scale_speed(speed):
    """Converts speed (0-MAX_SPEED) to PWM duty cycle (0-65535)."""
    clamped_speed = clamp(speed, 0, MAX_SPEED)
    pwm_value = int((clamped_speed / MAX_SPEED) * 65535)
    print(f"DEBUG: scale_speed({speed}) -> {pwm_value}")  # Debug print
    return pwm_value

def set_speed(left_speed, right_speed):
    """Sets motor speed with proper scaling."""
    left_duty = scale_speed(left_speed)
    right_duty = scale_speed(right_speed)

    print(f"DEBUG: Setting PWM - Left: {left_duty}, Right: {right_duty}")

    if not (0 <= left_duty <= 65535) or not (0 <= right_duty <= 65535):
        print("ERROR: PWM duty_cycle out of range!")
        return  # Prevent invalid PWM values

    left_pwm.duty_cycle = left_duty
    right_pwm.duty_cycle = right_duty

def move_forward(speed):
    """Moves both motors forward at the given speed."""
    if not motors_enabled:
        return
    left_dir.value = True
    right_dir.value = True
    set_speed(speed, speed)

def move_reverse(speed):
    """Moves both motors in reverse at the given speed."""
    if not motors_enabled:
        return
    left_dir.value = False
    right_dir.value = False
    set_speed(speed, speed)

def pivot_left(speed):
    """Pivots left with controlled sensitivity."""
    if not motors_enabled:
        return
    pivot_speed = clamp(speed, 0, MAX_SPEED)
    print(f"DEBUG: pivot_left called with pivot_speed={pivot_speed}")
    left_dir.value = False
    right_dir.value = True
    set_speed(pivot_speed, pivot_speed)

def pivot_right(speed):
    """Pivots right with controlled sensitivity."""
    if not motors_enabled:
        return
    pivot_speed = clamp(speed, 0, MAX_SPEED)
    print(f"DEBUG: pivot_right called with pivot_speed={pivot_speed}")
    left_dir.value = True
    right_dir.value = False
    set_speed(pivot_speed, pivot_speed)

def stop():
    """Gradually stops the motors without engaging brakes."""
    print("Stopping motors without braking")
    for i in range(RAMP_STEPS, 0, -1):
        left_pwm.duty_cycle = int(left_pwm.duty_cycle * (i / RAMP_STEPS))
        right_pwm.duty_cycle = int(right_pwm.duty_cycle * (i / RAMP_STEPS))
        time.sleep(RAMP_DELAY)
    left_pwm.duty_cycle = 0
    right_pwm.duty_cycle = 0
    print("Motors stopped, but brakes are not engaged")

def apply_brakes():
    """Explicitly engages brakes."""
    left_brake.value = True
    right_brake.value = True
    print("Brakes engaged")

def release_brakes():
    """Disengages brakes."""
    left_brake.value = False
    right_brake.value = False
    print("Brakes released")

def enable_motors(enable):
    """Enables or disables motor power."""
    global motors_enabled
    motors_enabled = enable
    if not enable:
        stop()
    print(f"Motors enabled: {motors_enabled}")
