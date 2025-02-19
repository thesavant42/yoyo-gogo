import board
import digitalio
import pwmio
import time
import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# === BLE Setup ===
ble = adafruit_ble.BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

# === Configuration ===
SPEED_LEVELS = [0.01, 0.02, 0.05, 0.1, 0.2]  # Define different speed levels
speed_index = 1  # Default speed level
PWM_FREQUENCY = 1000  # PWM frequency in Hz
MOVE_DURATION = 0.005  # Duration to run the motors on each command

# === Pin Assignments ===
PWM_R_PIN = board.D13
DIR_R_PIN = board.D12  
BRAKE_R_PIN = board.D11  
ENABLE_R_PIN = board.D10  
  
PWM_L_PIN = board.A0
DIR_L_PIN = board.A1  
BRAKE_L_PIN = board.A2  
ENABLE_L_PIN = board.A3  
  

# === Define Motor Control Pins ===
DIR_L = digitalio.DigitalInOut(DIR_L_PIN)
BRAKE_L = digitalio.DigitalInOut(BRAKE_L_PIN)
ENABLE_L = digitalio.DigitalInOut(ENABLE_L_PIN)
PWM_L = pwmio.PWMOut(PWM_L_PIN, frequency=PWM_FREQUENCY, duty_cycle=0)

DIR_R = digitalio.DigitalInOut(DIR_R_PIN)
BRAKE_R = digitalio.DigitalInOut(BRAKE_R_PIN)
ENABLE_R = digitalio.DigitalInOut(ENABLE_R_PIN)
PWM_R = pwmio.PWMOut(PWM_R_PIN, frequency=PWM_FREQUENCY, duty_cycle=0)

for pin in [DIR_L, BRAKE_L, ENABLE_L, DIR_R, BRAKE_R, ENABLE_R]:
    pin.direction = digitalio.Direction.OUTPUT

# === Motor Control Functions ===
brakes_engaged = False
dir_L_inverted = True
dir_R_inverted = False

def toggle_brakes():
    global brakes_engaged
    brakes_engaged = not brakes_engaged
    BRAKE_L.value = 1 if brakes_engaged else 0
    BRAKE_R.value = 1 if brakes_engaged else 0
    print(f"Brakes {'engaged' if brakes_engaged else 'released'}")

def toggle_dir_L():
    global dir_L_inverted
    dir_L_inverted = not dir_L_inverted
    print(f"Left Motor Direction Inverted: {dir_L_inverted}")

def toggle_dir_R():
    global dir_R_inverted
    dir_R_inverted = not dir_R_inverted
    print(f"Right Motor Direction Inverted: {dir_R_inverted}")

def set_speed(left_speed: float, right_speed: float, ramp_time=0.2):
    current_left = PWM_L.duty_cycle / 65535
    current_right = PWM_R.duty_cycle / 65535
    steps = 5
    delay = ramp_time / steps

    for i in range(1, steps + 1):
        easing_factor = (i / steps) ** 2
        PWM_L.duty_cycle = int(((current_left + (left_speed - current_left) * easing_factor) * 65535))
        PWM_R.duty_cycle = int(((current_right + (right_speed - current_right) * easing_factor) * 65535))
        time.sleep(delay)

    PWM_L.duty_cycle = int(left_speed * 65535)
    PWM_R.duty_cycle = int(right_speed * 65535)

def move(forward=True):
    left_speed = SPEED_LEVELS[speed_index]
    right_speed = SPEED_LEVELS[speed_index]

    ENABLE_L.value = 1
    ENABLE_R.value = 1
    DIR_L.value = (0 if forward else 1) if not dir_L_inverted else (1 if forward else 0)
    DIR_R.value = (0 if forward else 1) if not dir_R_inverted else (1 if forward else 0)
    BRAKE_L.value = 0
    BRAKE_R.value = 0
    print(f"Moving {'forward' if forward else 'backward'}")
    
    set_speed(left_speed, right_speed)
    time.sleep(MOVE_DURATION)
    stop()

def increase_speed():
    global speed_index
    if speed_index < len(SPEED_LEVELS) - 1:
        speed_index += 1
        print(f"Speed increased to {SPEED_LEVELS[speed_index]}")
    else:
        print("Speed is already at maximum")

def decrease_speed():
    global speed_index
    if speed_index > 0:
        speed_index -= 1
        print(f"Speed decreased to {SPEED_LEVELS[speed_index]}")
    else:
        print("Speed is already at minimum")

def pivot_left():
    left_speed = SPEED_LEVELS[speed_index]
    right_speed = SPEED_LEVELS[speed_index]

    ENABLE_L.value = 1
    ENABLE_R.value = 1
    DIR_L.value = 1 if not dir_L_inverted else 0  # Left wheel moves backward
    DIR_R.value = 0 if not dir_R_inverted else 1  # Right wheel moves forward
    BRAKE_L.value = 0
    BRAKE_R.value = 0
    print("Pivoting Left")

    set_speed(left_speed, right_speed)
    time.sleep(MOVE_DURATION)
    stop()

def pivot_right():
    left_speed = SPEED_LEVELS[speed_index]
    right_speed = SPEED_LEVELS[speed_index]

    ENABLE_L.value = 1
    ENABLE_R.value = 1
    DIR_L.value = 0 if not dir_L_inverted else 1  # Left wheel moves forward
    DIR_R.value = 1 if not dir_R_inverted else 0  # Right wheel moves backward
    BRAKE_L.value = 0
    BRAKE_R.value = 0
    print("Pivoting Right")

    set_speed(left_speed, right_speed)
    time.sleep(MOVE_DURATION)
    stop()

def stop():
    for i in range(10, 0, -1):
        PWM_L.duty_cycle = int(PWM_L.duty_cycle * (i / 10))
        PWM_R.duty_cycle = int(PWM_R.duty_cycle * (i / 10))
        time.sleep(0.05)

    PWM_L.duty_cycle = 0
    PWM_R.duty_cycle = 0
    ENABLE_L.value = 0
    ENABLE_R.value = 0
    print("Stopping: Motors disabled")

# === BLE Connection Handling ===
while True:
    if not ble.connected:
        print("Waiting for BLE connection...")
        ble.start_advertising(advertisement)
        while not ble.connected:
            pass
        print("BLE Connected! Waiting for commands...")

    while ble.connected:
        command = uart.readline()
        if command:
            command = command.decode("utf-8").strip()
            print(f"DEBUG: Received BLE command: {command}")

            if command.startswith("!B516!B507"):  # Forward
                move(forward=True)
            elif command.startswith("!B615!B606"):  # Backward
                move(forward=False)
            elif command.startswith("!B714!B705"):  # Left
                pivot_left()
            elif command.startswith("!B813!B804"):  # Right
                pivot_right()
            elif command.startswith("Button 5"):  # Stop
                stop()
            elif command.startswith("Button 6"):  # Increase Speed
                increase_speed()
            elif command.startswith("Button 7"):  # Decrease Speed
                decrease_speed()
            elif command.startswith("Button 8"):  # Toggle Brakes
                toggle_brakes()
            else:
                print("DEBUG: Invalid BLE Command Received -", command)
