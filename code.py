import time
import board
import digitalio
import pwmio
import sys

# --- Pin Setup ---
# Adjust these board pin names to match your wiring.

# Enable: Always HIGH
enable_pin = digitalio.DigitalInOut(board.D10)
enable_pin.direction = digitalio.Direction.OUTPUT
enable_pin.value = True

# Brake: LOW by default (disengaged)
brake_pin = digitalio.DigitalInOut(board.D11)
brake_pin.direction = digitalio.Direction.OUTPUT
brake_pin.value = False

# Direction: HIGH = forward by default
direction_pin = digitalio.DigitalInOut(board.D12)
direction_pin.direction = digitalio.Direction.OUTPUT
direction_pin.value = True

# PWM output (e.g., connected to your ESC’s PWM input)
# The duty_cycle property in CircuitPython is a 16-bit value (0 to 65535).
pwm = pwmio.PWMOut(board.D13, frequency=2000, duty_cycle=0)

# --- PWM Mapping ---
# These constants define the minimum and maximum PWM duty values for your ESC.
# You may need to adjust these so that 0% speed gives PWM_MIN and 100% gives PWM_MAX.
PWM_MIN = 3277   # For example, about 5% of 65535
PWM_MAX = 9830   # For example, about 15% of 65535

def map_speed_to_duty(speed_percent):
    """Map a speed (0-100%) to a PWM duty cycle value between PWM_MIN and PWM_MAX."""
    if speed_percent < 0:
        speed_percent = 0
    elif speed_percent > 100:
        speed_percent = 100
    # Linear mapping:
    duty = PWM_MIN + int((PWM_MAX - PWM_MIN) * (speed_percent / 100.0))
    return duty

# --- Command Parsing ---
def parse_command(cmd):
    """
    Parse a command string and set the motor parameters.
    Expected command formats:
      s <speed>       e.g., "s 50" sets speed to 50%
      d <direction>   e.g., "d forward" or "d reverse"
      b <brake>       e.g., "b on" or "b off"
    """
    cmd = cmd.strip()
    if not cmd:
        return

    tokens = cmd.split()
    if len(tokens) < 2:
        print("Invalid command. Format: s <0-100>, d <forward|reverse>, or b <on|off>")
        return

    command = tokens[0].lower()
    arg = tokens[1].lower()

    if command == "s":
        # Set speed
        try:
            speed = int(arg)
        except ValueError:
            print("Invalid speed value.")
            return
        duty = map_speed_to_duty(speed)
        pwm.duty_cycle = duty
        print("Speed set to {}% (PWM duty: {})".format(speed, duty))

    elif command == "d":
        # Set direction
        if arg == "forward":
            direction_pin.value = True
            print("Direction set to forward")
        elif arg == "reverse":
            direction_pin.value = False
            print("Direction set to reverse")
        else:
            print("Invalid direction. Use 'forward' or 'reverse'.")

    elif command == "b":
        # Engage/disengage brake
        if arg == "on":
            brake_pin.value = True
            print("Brake engaged")
        elif arg == "off":
            brake_pin.value = False
            print("Brake disengaged")
        else:
            print("Invalid brake command. Use 'on' or 'off'.")

    else:
        print("Unknown command.")

# --- Main Program Loop ---
print("ZS-X11H BLDC Motor Driver (CircuitPython Version)")
print("Enter commands over the serial console using the following format:")
print("  s <0-100>      (set speed percentage)")
print("  d <forward|reverse>   (set direction)")
print("  b <on|off>     (engage/disengage brake)")

while True:
    # Read a line from the serial console if available.
    # Note: In CircuitPython, sys.stdin.readline() blocks until a line is available.
    cmd = sys.stdin.readline()
    if cmd:
        parse_command(cmd)
    time.sleep(0.1)
