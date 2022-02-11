# smartglove-pi

## Configuration

On Raspberry-Pi:
- Install the right packages for bluetooth
- Installation of Home Assistant using Docker on a Raspberry Pi
- Add a connected lamp using Tuya integration for instance (follow the Home Assistant tutorial)

To use MQTT (optional):
- Install Mosquitto
- Check ports are open in the local network (8123, 1883 : do not hesitate to edit configuration files)
- Configure the MQTT server
- Create a custom script (call service mqtt.publish)
- Edit the home panel to add a button for the lamp and the custom script

## Usage

1. Start the iGlove-arduino main project (cf related readme file) on Arduino Nano
3. Start the iGlove-arduino iDevice project on Arduino (optional)
2. Start ble_connect_2.py on Raspberry Pi 1
5. Check everything is connected
