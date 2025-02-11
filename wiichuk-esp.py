import time
import board
import adafruit_nunchuk
import wifi
import espnow

# Initialize I2C using the built-in STEMMA QT connector
i2c = board.STEMMA_I2C()  # Uses built-in STEMMA QT connector

# Initialize the Nunchuk
nc = adafruit_nunchuk.Nunchuk(i2c)

# Initialize ESP-NOW
esp = espnow.ESPNow()

# Ensure the peer MAC address is exactly 6 bytes long
peer_mac = b'\xAA\xBB\xCC\xDD\xEE\xFF'  # Corrected MAC address (6 bytes)

# Add peer
peer = espnow.Peer(peer_mac)
esp.peers.append(peer)

# Retrieve and print the MAC address of the MCU
mac_address = wifi.radio.mac_address
print("MAC Address:", ":".join(f"{b:02X}" for b in mac_address))

# Track button states to prevent repeated sends
previous_c_state = False
previous_z_state = False

while True:
    try:
        # Read joystick positions
        x, y = nc.joystick
        print(f"Joystick position: x={x}, y={y}")

        # Read acceleration data
        ax, ay, az = nc.acceleration
        print(f"Acceleration: ax={ax}, ay={ay}, az={az}")

        # Check button states
        current_c_state = nc.buttons.C
        current_z_state = nc.buttons.Z

        # Send messages only on state change
        if current_c_state and not previous_c_state:
            print("Button C pressed")
            esp.send(peer, b'Button C pressed')  # Now sending to Peer object, not bytes
        if current_z_state and not previous_z_state:
            print("Button Z pressed")
            esp.send(peer, b'Button Z pressed')  # Now sending to Peer object, not bytes

        # Update previous states
        previous_c_state = current_c_state
        previous_z_state = current_z_state

    except Exception as e:
        print("An error occurred:", e)

    time.sleep(0.1)  # Reduced sleep time for better responsiveness
