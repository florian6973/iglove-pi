# smartglove-pi

## Configuration

On Raspberry-Pi 1:
- Install the right packages for bluetooth

On Raspberry-Pi 2:
- Installation using Docker on a Raspberry Pi
- Install Mosquitto
- Check ports are open in the local network (8123, 1883 : do not hesitate to edit configuration files)
- Add a connected lamp using Tuya integration for instance (follow HA tutorial)
- Configure the MQTT server
- Create a custom script (call service mqtt.publish)
- Edit the home panel to add a button for the lamp and the custom script

## Usage

1. Start the iGlove-arduino main project (cf related readme file) on Arduino Nano
3. Start the iGlove-arduino iDevice project on Arduino
2. Start ble_connect.py on Raspberry Pi 1
4. Start CustomObjectPI.py, CustomObjectArduino.py on Raspberry Pi 2
5. Check everything is connected
