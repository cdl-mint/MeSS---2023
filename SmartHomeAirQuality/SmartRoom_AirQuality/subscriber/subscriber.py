import paho.mqtt.client as mqtt
import time
import logging
import json
import requests

LOGGER = logging.getLogger()
##CHANGE URL HERE IF NECESSARY##
BASE_URL = "http://simplerest:8001/Rooms/"

def on_message(client, userdata, message):

    #Read devices from json on every message - in case a new device was added
    with open("devices.json", "r") as f:
        devices = json.load(f)
    
    key_list = list(devices.keys())
    
    device = message.topic[12:]
      
    #Is the current message in a topic the subscriber is listening to?
    if device in key_list:
        
        #Get information about the device that sent a message
        try:
            device_group = devices[device]["device_type"]
            device_room = devices[device]["device_room"]
            payload = json.loads(str(message.payload.decode("utf-8")))

            # store the event state via the api according to the device type
            if device_group == "Lights":
                data = {}
                if payload["state"] == "OFF":
                    data["turnon"] = False
                else:
                    data["turnon"] = True
                    
                data["brightness"] = int(payload["brightness"])
                data["color_x"] = float(payload["color"]["x"])
                data["color_y"] = float(payload["color"]["y"])

                
                res = requests.post(
                    f"{BASE_URL}{device_room}/Lights/{device}/Activation", json=data)
            
            elif device_group == "Motion_Sensors":
                data = {}
                data["detection"] = bool(payload["occupancy"])
                

                res = requests.post(
                    f"{BASE_URL}{device_room}/Motion_Sensors/{device}/Operations", json=data)

            elif device_group == "Ventilators":
                data = {}
                if payload["state"] == "OFF":
                    data["turnon"] = False
                else:
                    data["turnon"] = True
                
                res = requests.post(
                    f"{BASE_URL}{device_room}/Ventilators/{device}/Operations", json=data)


            ##For this project the remote is not maintained on the API level - it is just used here to map actions to the buttons##
            elif device_group == "Remote":
                
                command = payload["action"]
                if command == "emergency":
                    ##DEFINE HERE WHAT TO DO ON EMERGENCY BUTTON##
                    requests.post(f"{BASE_URL}1/Lights/Licht/Activation")

                elif command == "arm_all_zones":
                    ##DEFINE HERE WHAT TO DO ON ARM ALL ZONES BUTTON##
                    requests.post(f"{BASE_URL}1/Power_Plugs/PowerPlug1/Activation")

                elif command == "arm_day_zones":
                    ##DEFINE HERE WHAT TO DO ON ALL ZONES BUTTON##
                    requests.post(f"{BASE_URL}1/Power_Plugs/PowerPlug2/Activation")

                elif command == "disarm":
                    ##DEFINE HERE WHAT TO DO ON DISARM##
                    print("No Operation set")

        except KeyError:
            print("Key {device} was not found")
            
            

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt broker!")

    # use # as multiple level wildcard and + as single level wildcard
    client.subscribe("zigbee2mqtt/#")


client = mqtt.Client("subscriber_docker")
client.on_message = on_message
client.on_connect = on_connect

##CHANGE IP ADDRESS HERE##
client.connect("10.78.42.10", 1883, 60)
client.loop_forever()
