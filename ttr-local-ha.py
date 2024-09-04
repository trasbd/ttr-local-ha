import sys
import paho.mqtt.client as mqtt

if __name__ == '__main__':
    # MQTT broker details
    broker_address = "homeassistant.local"
    broker_port = 1883  # Default MQTT port

    # Callback function for when the client connects to the broker
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    # Create a client instance
    client = mqtt.Client()
    client.on_connect = on_connect

    # Connect to the broker
    client.connect(broker_address, broker_port)

    # Publish a message to the topic "my/topic"
    client.publish("my/topic", "Hello from Python!")

    # Disconnect from the broker
    client.disconnect()


def get_laff():
    import requests
    api_url = "http://localhost:1547/info.json"
    headers = {"Authorization": "Bearer MYREALLYLONGTOKENIGOT",
               'User-Agent': 'My User Agent 1.0',}

    myRes = requests.get(api_url, headers=headers)
    return myRes.json()['laff']['current']


def write_message_to_console(message):
    print(message)
    sys.stdout.flush()

