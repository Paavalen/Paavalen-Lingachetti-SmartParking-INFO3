#!/bin/bash

check_exit_status() {
    if [ $? -ne 0 ]; then
        echo "Error occurred. Exiting."
        exit 1
    fi
}

echo "Updating package lists..."
sudo apt-get update
check_exit_status

echo "Installing Python 3 and pip..."
sudo apt-get install -y python3 python3-pip
check_exit_status

echo "Installing Python dependencies..."
pip3 install flask Flask-SQLAlchemy flask-login pyserial qrcode[pil]
check_exit_status

echo "Installing Arduino CLI..."
sudo apt-get install -y arduino arduino-mk
check_exit_status

echo "Installing additional tools..."
sudo apt-get install -y git curl
check_exit_status

echo "All dependencies have been installed successfully."
echo "Setup completed. You can now run your project."
