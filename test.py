import serial
import time

SERIAL_PORT = 'COM9'
BAUD_RATE = 9600
TIMEOUT = 2
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5

def test_serial_connection():
    for attempt in range(RETRY_ATTEMPTS):
        try:
            # Open the serial port
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
            print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
            
            # Wait for Arduino to reset
            time.sleep(2)
            
            # Send a test message to Arduino
            test_message = "TEST"
            ser.write(test_message.encode())
            print(f"Sent: {test_message}")

            # Read the response from Arduino
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                print(f"Received: {response}")
            else:
                print("No response received.")

            # Close the serial connection
            ser.close()
            break  # Exit the loop if successful

        except serial.SerialException as e:
            print(f"Error: {e}")
            print(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

if __name__ == "__main__":
    test_serial_connection()
