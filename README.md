# yoyo-gogo
CircuitPython scrfipts to assist with robot mobility

## Pin Configuration
Each ZSX11H motor driver has the following key input pins:
1. **PWM**: Controls the speed of the motor.
2. **DIR**: Sets the motor rotation direction (clockwise/counterclockwise).
3. **BRAKE**: Activates the brake mechanism.
4. **STOP**: Halts the motor.
5. **GND**: Common ground.

### Arduino Pin Assignments

#### LEFT MOTOR 
| Arduino Pin | Motor Driver Pin | Description                   |
|-------------|------------------|-------------------------------|
| A0          | PWM_L            | Speed control for left motor |
| A1          | DIR_L            | Direction control for left motor|
| A2          | BRAKE_L          | Brake control for left motor |
| A3          | STOP_L           | Stop control for left motor  |
| A4          | L_Speed          | Speed Pulse for left motor   |
| True        | Fwd_L_Logic      | Is "Fwd" correct? Invert if not |
|-------------|------------------|-------------------------------|

#### RIGHT MOTOR 
| Arduino Pin | Motor Driver Pin | Description                   |
|-------------|------------------|-------------------------------|
| D9          | PWM_R            | Speed control for right motors|
| D10         | STOP_R           | Stop control for right motors |
| D11         | BRAKE_R          | Brake control for right motors|
| D12         | DIR_R            | Direction control for right motors|
| D13         | R_Speed          | Speed pulse for right motors  |
| False       | Fwd_R_Logic      | Is "Fwd" correct? Invert if not |
