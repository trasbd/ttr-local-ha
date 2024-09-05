import paho.mqtt.client as mqtt
import time
import requests

# mySecrets.py contains MQTT username and password
import mySecrets


def get_ttr_info():
    myRes = None
    api_url = "http://localhost:1547/info.json"
    headers = {
        "Authorization": "Bearer MYREALLYLONGTOKENIGOT",
        "User-Agent": "ttr-local-ha",
    }
    try:
        myRes = requests.get(api_url, headers=headers)
        return myRes
    except:
        return None


def my_loop():
    ttr_info = get_ttr_info()
    if ttr_info != None:
        if ttr_info.status_code == 200:
            ttr_json = ttr_info.json()
            client.publish(
                "sensor/" + ttr_json["toon"]["name"].replace(" ", ""), ttr_info.content
            )
            print(ttr_json["toon"]["name"] + " " + str(ttr_json["laff"]["current"])+ " / " + str(ttr_json["laff"]["max"]))
        else:
            print("Connected to TTR with result code " + ttr_info.status_code)
    else:
        print("TTR not running")
    time.sleep(5)


if __name__ == "__main__":
    # MQTT broker details
    broker_address = "homeassistant.local"
    broker_port = 1883  # Default MQTT port

    # Callback function for when the client connects to the broker
    def on_connect(client, userdata, flags, rc, prop=None):
        print("Connected to HA with result code " + str(rc))

    def on_disconnect(client, userdata, flags, rc, prop=None):
        print("Disconnect from HA with result code " + str(rc))

    # Create a client instance
    print("Starting")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "ttr-local-ha2")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # from mySecrets.py
    client.username_pw_set(mySecrets.username, mySecrets.password)

    # Connect to the broker
    client.connect(broker_address, broker_port)

    client.loop_start()

    while True:
        my_loop()

    client.loop_stop()
    client.disconnect()
