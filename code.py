import time
import board
import pwmio
import digitalio

# Pin Definitions
enable_pin = digitalio.DigitalInOut(board.D10)
enable_pin.direction = digitalio.Direction.OUTPUT

brake_pin = digitalio.DigitalInOut(board.D11)
brake_pin.direction = digitalio.Direction.OUTPUT

direction_pin = digitalio.DigitalInOut(board.D12)
direction_pin.direction = digitalio.Direction.OUTPUT

pwm_motor = pwmio.PWMOut(board.D13, frequency=1000, duty_cycle=10, variable_frequency=True)

# Constants
MIN_SPEED = 100 # Hz
MAX_SPEED = 1000  # Hz
SPEED_STEP = 100   # Hz increment
RAMP_DELAY = .1     # Seconds


def print_motor_state(speed):
    print(f"PWM Frequency: {pwm_motor.frequency} Hz")
    print(f"Direction: {'Forward' if direction_pin.value else 'Reverse'}")
    print(f"Brake: {'Engaged' if not brake_pin.value else 'Released'}")
    print(f"Enable: {'ON' if enable_pin.value else 'OFF'}")
    print(f"Current Speed: {speed} Hz")
    print("--------------------------------")


def drive_motor():
    try:
        direction_pin.value = False  # Set direction forward
        enable_pin.value = True     # Enable motor
        brake_pin.value = False     # Release brake
        
        print_motor_state(MIN_SPEED)

        # Ramp up speed
        current_speed = MIN_SPEED
        while current_speed <= MAX_SPEED:
            pwm_motor.frequency = current_speed
            print_motor_state(current_speed)
            time.sleep(RAMP_DELAY)
            current_speed += SPEED_STEP

        # Ramp down speed
        while current_speed > 1000:
            current_speed -= SPEED_STEP
            pwm_motor.frequency = max(current_speed, 0)
            print_motor_state(current_speed)
            time.sleep(RAMP_DELAY)

        # Stop motor and disable
        pwm_motor.frequency = MIN_SPEED  # Ensure motor stops
        enable_pin.value = False  # Allow motor to coast
        
        print_motor_state(0)
    
    except Exception as e:
        print(f"Error occurred: {e}")
         # Stop motor and disable
        pwm_motor.frequency = MIN_SPEED  # Ensure motor stops
        enable_pin.value = False  # Allow motor to coast

if __name__ == "__main__":
    drive_motor()
