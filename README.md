# Smart Parking

The Smart Parking project is designed to streamline parking management using modern technology. By integrating sensors, an Arduino, and a web interface built with Flask, this system allows users to reserve parking spots in real time. The system includes features like dynamic slot availability, QR code generation use for entry pass, and automated control of parking spot indicators.

## Setup & Installation

### 1. Clone the Repository
First, clone the repository into your Raspberry Pi:

```bash
git clone https://github.com/Paavalen/Paavalen-Lingachetti-SmartParking-INFO3.git
```

### 2. Navigate to the Project Directory
Open a terminal and navigate to the project directory:

### 3. Ensure the Script's Execution Rights
Ensure the installation script `install.sh` has execution rights:

```bash
chmod +x install.sh
```

### 4. Install Dependencies
Run the installation script to install all necessary dependencies:

```bash
./install.sh
```
### 5. Setup Arduino
Install arduino IDE on your Raspberry Pi or on another PC then upload the sketch in the Arduino folder

if you used another pc, unplug the Arduino and plug it into the Raspberry Pi

## Running The App

Once the dependencies are installed, you can start the application:

```bash
python3 main.py
```

## Viewing The App

Open a web browser and go to:

```
http://127.0.0.1:5000
```
