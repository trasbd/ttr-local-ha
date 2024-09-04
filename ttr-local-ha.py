import paho.mqtt.client as mqtt
import time
import requests
import mySecrets

def get_ttr_info():
    myRes = None
    api_url = "http://192.168.86.50:1547/info.json"
    headers = {"Authorization": "Bearer MYREALLYLONGTOKENIGOT",
               'User-Agent': 'My User Agent 1.0',}
    try:
        myRes = requests.get(api_url, headers=headers)
        return myRes
    except:
        return None
    
    

def my_loop():
    ttr_info = get_ttr_info()
    if(ttr_info != None):
        if(ttr_info.status_code == 200):
            ttr_json = ttr_info.json()
            client.publish("sensor/"+ttr_json["toon"]["name"].replace(" ", ""), ttr_info.content)
            print(ttr_json["toon"]["name"])
        else:
            print(ttr_info.status_code)
    else:
        print("TTR not running")
    time.sleep(15)
     

if __name__ == '__main__':
    # MQTT broker details
    broker_address = "homeassistant.local"
    broker_port = 1883  # Default MQTT port



   
    # Callback function for when the client connects to the broker
    def on_connect( client, userdata, flags, rc, prop=None):
        print("Connected with result code " + str(rc))
        

    # Create a client instance
    print("Starting")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,"ttr-local-ha")
    client.on_connect = on_connect
    
    client.username_pw_set(mySecrets.username, mySecrets.password)
    # Connect to the broker
    client.connect(broker_address, broker_port)

    client.loop_start()

    while True:
        my_loop()




    # Publish a message to the topic "my/topic"

    

    # Disconnect from the broker
    #client



