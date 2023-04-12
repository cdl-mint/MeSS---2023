import paho.mqtt.client as mqtt
import time
import logging
import json


TOPIC = ""
DATA = {}
#****Change Host IP if necessary here****
MOSQUITTO_HOST = "10.78.42.10"
CLIENT_NAME = "publisher"

def publish_message(topic, data):

    #set the values
    global TOPIC
    global DATA

    TOPIC = topic
    DATA = data

    #create the client to publish the message
    client = mqtt.Client(CLIENT_NAME)

    #set the callback method
    client.on_connect=on_connect

    #connect to the client
   
    client.connect(MOSQUITTO_HOST, 1883, 60)
    

    #ensure the connection stays active till the message has been sent
    client.loop_forever()


def on_connect(client, userdata, flags, rc):
    
    #After connection is established, publish the message
    publish_data(client)


def publish_data(client):

    client.publish(TOPIC, payload = json.dumps(DATA), qos = 0, retain=False)

    #close the connection after sending
    client.disconnect()





