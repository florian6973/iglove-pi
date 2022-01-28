import paho.mqtt.client as mqtt
from gpiozero import LED
from time import sleep

ledPin = 2
mqtt_server = "172.16.16.8"
topic = "default"

led = LED(ledPin)
led.off()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic)
    

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    print("\tClignote")
    led.blink(0.1)
    sleep(3)
    led.off()
    print("\tClignoté")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_server, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
