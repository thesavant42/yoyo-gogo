import board
import digitalio
import pwmio
import time
import sys


## end testing
# === Configuration ===
SPEED_LEVELS = [0.05, 0.1, 0.2, 0.3, 0.5]  # Define different speed levels
speed_index = 2  # Default speed level (middle of the list)
THROTTLE_SENSITIVITY = 0.05  # Adjusted for lower speed control
PWM_FREQUENCY = 1000  # PWM frequency in Hz
MOVE_DURATION = 0.01  # Duration to run the motors on each key press (in seconds)

# === Pin Assignments ===
DIR_R_PIN = board.D12  # Direction control for left motor
BRAKE_R_PIN = board.D11  # Brake control for left motor
ENABLE_R_PIN = board.D10  # Enable control for left motor
PWM_R_PIN = board.D13  # PWM control for left motor speed

DIR_L_PIN = board.A1  # Direction control for right motor
BRAKE_L_PIN = board.A2  # Brake control for right motor
ENABLE_L_PIN = board.A3  # Enable control for right motor
PWM_L_PIN = board.A0  # PWM control for right motor speed

# === Define Motor Control Pins ===
DIR_L = digitalio.DigitalInOut(DIR_L_PIN)
BRAKE_L = digitalio.DigitalInOut(BRAKE_L_PIN)
ENABLE_L = digitalio.DigitalInOut(ENABLE_L_PIN)
PWM_L = pwmio.PWMOut(PWM_L_PIN, frequency=PWM_FREQUENCY, duty_cycle=0)

DIR_R = digitalio.DigitalInOut(DIR_R_PIN)
BRAKE_R = digitalio.DigitalInOut(BRAKE_R_PIN)
ENABLE_R = digitalio.DigitalInOut(ENABLE_R_PIN)
PWM_R = pwmio.PWMOut(PWM_R_PIN, frequency=PWM_FREQUENCY, duty_cycle=0)

# Configure pins as outputs
for pin in [DIR_L, BRAKE_L, ENABLE_L, DIR_R, BRAKE_R, ENABLE_R]:
    pin.direction = digitalio.Direction.OUTPUT

# === Motor Control Functions ===

# Brake toggle state
brakes_engaged = False

def toggle_brakes():
    """ Toggles the brakes for both left and right motors. """
    global brakes_engaged
    brakes_engaged = not brakes_engaged
    BRAKE_L.value = 1 if brakes_engaged else 0
    BRAKE_R.value = 1 if brakes_engaged else 0
    print(f"Brakes {'engaged' if brakes_engaged else 'released'}")

# Direction Inversion Flags
dir_L_inverted = True
dir_R_inverted = False

def toggle_dir_L():
    """ Toggles the direction logic for the left motor """
    global dir_L_inverted
    dir_L_inverted = not dir_L_inverted
    print(f"Left Motor Direction Inverted: {dir_L_inverted}")

def toggle_dir_R():
    """ Toggles the direction logic for the right motor """
    global dir_R_inverted
    dir_R_inverted = not dir_R_inverted
    print(f"Right Motor Direction Inverted: {dir_R_inverted}")

def set_speed(left_speed: float, right_speed: float, ramp_time=0.5):
    """ Gradually ramps the motor speed up or down to avoid abrupt movements """
    current_left = PWM_L.duty_cycle / 65535
    current_right = PWM_R.duty_cycle / 65535
    steps = 10  # Number of steps in the ramp
    delay = ramp_time / steps

    for i in range(1, steps + 1):
        # Use a quadratic easing function for smooth acceleration
        easing_factor = (i / steps) ** 2
        PWM_L.duty_cycle = int(((current_left + (left_speed - current_left) * easing_factor) * 65535))
        PWM_R.duty_cycle = int(((current_right + (right_speed - current_right) * easing_factor) * 65535))
        time.sleep(delay)

def move(left_speed=SPEED_LEVELS[speed_index], right_speed=SPEED_LEVELS[speed_index], forward=True):
    """ Moves the robot at given speed and direction for a fixed duration. """
    ENABLE_L.value = 1  # Enable motors
    ENABLE_R.value = 1
    DIR_L.value = (0 if forward else 1) if not dir_L_inverted else (1 if forward else 0)
    DIR_R.value = (0 if forward else 1) if not dir_R_inverted else (1 if forward else 0)
    BRAKE_L.value = 0
    BRAKE_R.value = 0
    print(f"Moving {'forward' if forward else 'backward'}: Left speed = {left_speed}, Right speed = {right_speed}")
    set_speed(left_speed, right_speed)
    time.sleep(MOVE_DURATION)
    stop()

def stop():
    """ Gradually stops the motors instead of abrupt braking """
    for i in range(10, 0, -1):  # Gradual deceleration
        PWM_L.duty_cycle = int(PWM_L.duty_cycle * (i / 10))
        PWM_R.duty_cycle = int(PWM_R.duty_cycle * (i / 10))
        time.sleep(0.05)  # Short delay for smoother stopping
    ENABLE_L.value = 0  # Disable motors
    ENABLE_R.value = 0  # Disable motors
    BRAKE_L.value = 1  # Engage brakes
    BRAKE_R.value = 1  # Engage brakes
    print("Stopping: Motors disabled, Brakes engaged")
    time.sleep(0.1)  # Ensure braking takes effect

def pivot_left():
    """ Spins the robot in place to the left by moving wheels in opposite directions at equal speed. """
    ENABLE_L.value = 1  # Enable motors
    ENABLE_R.value = 1
    DIR_L.value = (1 if not dir_L_inverted else 0)  # Left wheel moves backward
    DIR_R.value = (0 if not dir_R_inverted else 1)  # Right wheel moves forward
    BRAKE_L.value = 0
    BRAKE_R.value = 0
    print("Pivoting Left: Left motor backward, Right motor forward")
    set_speed(0.3, 0.3)  # Ensure both motors move at the same speed
    time.sleep(MOVE_DURATION)
    stop()

def pivot_right():
    """ Spins the robot in place to the right by moving wheels in opposite directions at equal speed. """
    ENABLE_L.value = 1  # Enable motors
    ENABLE_R.value = 1
    DIR_L.value = (0 if not dir_L_inverted else 1)  # Left wheel moves forward
    DIR_R.value = (1 if not dir_R_inverted else 0)  # Right wheel moves backward
    BRAKE_L.value = 0
    BRAKE_R.value = 0
    print("Pivoting Right: Left motor forward, Right motor backward")
    set_speed(0.3, 0.3)  # Ensure both motors move at the same speed
    time.sleep(MOVE_DURATION)
    stop()

# === Serial Control ===
print("Starting Serial Control... Use keys to control the robot.")
print("B: Toggle Brakes")
print("W: Forward, S: Backward, A: Left, D: Right, X: Stop, +: Increase Speed, -: Decrease Speed, L: Toggle Left Dir, R: Toggle Right Dir")

def increase_speed():
    global speed_index
    if speed_index < len(SPEED_LEVELS) - 1:
        speed_index += 1
    print(f"Speed increased: {SPEED_LEVELS[speed_index]}")

def decrease_speed():
    global speed_index
    if speed_index > 0:
        speed_index -= 1
    print(f"Speed decreased: {SPEED_LEVELS[speed_index]}")

while True:
    command = sys.stdin.read(1).strip().upper()
    if command == "W":
        move(SPEED_LEVELS[speed_index], SPEED_LEVELS[speed_index], forward=True)
    elif command == "S":
        move(SPEED_LEVELS[speed_index], SPEED_LEVELS[speed_index], forward=False)
    elif command == "A":
        pivot_left()
    elif command == "D":
        pivot_right()
    elif command == "X":
        stop()
    elif command == "+":
        increase_speed()
    elif command == "-":
        decrease_speed()
    elif command == "L":
        toggle_dir_L()
    elif command == "R":
        toggle_dir_R()
    elif command == "B":
        toggle_brakes()
    else:
        print("Invalid command. Use W, S, A, D, X, +, -, L, or R.")
