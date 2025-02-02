import time
import board
import pwmio
import digitalio

# Pin Definitions for Motor 1
enable_pin1 = digitalio.DigitalInOut(board.D10)
enable_pin1.direction = digitalio.Direction.OUTPUT

brake_pin1 = digitalio.DigitalInOut(board.D11)
brake_pin1.direction = digitalio.Direction.OUTPUT

direction_pin1 = digitalio.DigitalInOut(board.D12)
direction_pin1.direction = digitalio.Direction.OUTPUT

pwm_motor1 = pwmio.PWMOut(board.D13, frequency=1000, duty_cycle=0)

# Pin Definitions for Motor 2
enable_pin2 = digitalio.DigitalInOut(board.A3)
enable_pin2.direction = digitalio.Direction.OUTPUT

brake_pin2 = digitalio.DigitalInOut(board.A2)
brake_pin2.direction = digitalio.Direction.OUTPUT

direction_pin2 = digitalio.DigitalInOut(board.A1)
direction_pin2.direction = digitalio.Direction.OUTPUT

pwm_motor2 = pwmio.PWMOut(board.A0, frequency=1000, duty_cycle=0)

# Constants
MIN_SPEED = 1000  # Hz
MAX_SPEED = 2000  # Hz
SPEED_STEP = 100  # Hz increment
RAMP_DELAY = 2    # Seconds

def print_motor_state(speed, motor_id):
    print(f"Motor {motor_id} - PWM Frequency: {speed} Hz")
    print(f"Motor {motor_id} - Direction: {'Forward' if motor_id == 1 and direction_pin1.value else 'Forward' if motor_id == 2 and direction_pin2.value else 'Reverse'}")
    print(f"Motor {motor_id} - Brake: {'Engaged' if motor_id == 1 and not brake_pin1.value else 'Engaged' if motor_id == 2 and not brake_pin2.value else 'Released'}")
    print(f"Motor {motor_id} - Enable: {'ON' if motor_id == 1 and enable_pin1.value else 'ON' if motor_id == 2 and enable_pin2.value else 'OFF'}")
    print("--------------------------------")

def drive_motors():
    try:
        # Set direction forward for both motors
        direction_pin1.value = True
        direction_pin2.value = True

        # Enable both motors
        enable_pin1.value = True
        enable_pin2.value = True

        # Release brake for both motors
        brake_pin1.value = False
        brake_pin2.value = False

        print_motor_state(MIN_SPEED, 1)
        print_motor_state(MIN_SPEED, 2)

        # Ramp up speed
        current_speed = MIN_SPEED
        while current_speed <= MAX_SPEED:
            pwm_motor1.frequency = current_speed
            pwm_motor2.frequency = current_speed
            print_motor_state(current_speed, 1)
            print_motor_state(current_speed, 2)
            time.sleep(RAMP_DELAY)
            current_speed += SPEED_STEP

        # Ramp down speed
        while current_speed > 0:
            current_speed -= SPEED_STEP
            pwm_motor1.frequency = max(current_speed, 0)
            pwm_motor2.frequency = max(current_speed, 0)
            print_motor_state(current_speed, 1)
            print_motor_state(current_speed, 2)
            time.sleep(RAMP_DELAY)

        # Stop motors and disable
        pwm_motor1.frequency = MIN_SPEED  # Ensure motor stops
        pwm_motor2.frequency = MIN_SPEED  # Ensure motor stops
        enable_pin1.value = False  # Allow motor to coast
        enable_pin2.value = False  # Allow motor to coast

        print_motor_state(0, 1)
        print_motor_state(0, 2)

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    drive_motors()
