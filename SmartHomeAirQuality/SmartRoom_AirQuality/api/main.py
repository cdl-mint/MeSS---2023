from ast import And
from enum import Enum
import json
import os
from asyncio.log import logger
from datetime import datetime,timedelta
import uvicorn
import asyncio
from fastapi import Depends,FastAPI, HTTPException, status,Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from session import db_Session,settings
from databases import Database
from schema import UserDetails,DigitalTwins,Room,PeopleInRoom,Light, Light_Operation, Power_Plug, Power_Plug_Operation,Airqualityproperty
from fastAPI_models import UserInfoBase,UserCreate,Token,UserAuthenticate,DigitalTwin_Object,Room_Object, Update_RoomObject, Lights_Object, Light_Operation_Object, Light_Operation_Return_Object, Update_LightObject, Time_Query_Object, Light_Operation_Storing_Object, Power_Plug_Object, Power_Plug_Update_Object, Power_Plug_Operation_Object, Power_Plug_Storing_Object,AirQuality_Properties_Object,AirQuality_Co2_Object,AirQuality_Temperature_Object,AirQuality_Humidity_Object,PeopleInRoomObject,Light_Activation_Object
from typing import List,Union
from sqlalchemy import and_, text,update
from publisher import publish_message
from passlib.context import CryptContext
from fastapi_pagination import Page, paginate, add_pagination
import bcrypt
import auth
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY =settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

tags_metadata = [
  {
    "name":"DT",
    "description":"Create and manage digital twins with its capabilities"
  },

    {
        "name": "Rooms",
        "description": "CRUD operations on room",
    },
    {
        "name": "Lights",
        "description": "Add lights in room, operate them (turn on/off) and change colors (use only hex color code)",
        "externalDocs": {
            "description": "sample hex color code",
            "url": "https://htmlcolorcodes.com/",
        },
    },
    {
        "name": "Ventilators",
        "description": "Attach ventilators to smart plug and operate them (turn on/off) based on indoor air quality",
        
    },
    {
        "name": "Doors",
        "description": "CRUD operations on doors- Not implemented",
    },
    {
        "name": "Windows",
        "description": "CRUD operations on windows- Not implemented",
    },
    {
        "name": "AirQuality",
        "description": "CRUD operations on air quality measurements (co2, temperature and humidity) in room",
        
    },
]
#oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION, openapi_tags=tags_metadata, root_path="/smartroomairquality-test")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
add_pagination(app)
#DT's
@app.post("/DigitalTwin", tags=["DT"], response_model=DigitalTwin_Object, status_code=status.HTTP_201_CREATED)
async def add_DT(addDT: DigitalTwin_Object):
    db_classes = DigitalTwins(dt_id=addDT.dt_id,dt_type=addDT.dt_type,dt_location=addDT.dt_location, dt_active_status=addDT.dt_active_status,dt_capability=addDT.dt_capability)
    try:
        db_Session.add(db_classes)
        db_Session.flush()
        db_Session.commit()
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
    return addDT

"""Returns all the dt's present in the database"""
@app.get("/DigitalTwins", tags=["DT"],response_model=List[DigitalTwin_Object], status_code=status.HTTP_200_OK)
async def get_All_DTs():
    results = db_Session.query(DigitalTwins).all()
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'No twins are available')
    else: 
        return results
# Rooms
"""Creates a new room in the database and returns the room on success. Room_id needs to be unique"""
"""Example room object 
{
    "room_id": 1,
    "room_size": 50,
    "measurement_unit":"50 sq.m"
}"""
@app.post("/Rooms", tags=["Rooms"], response_model=Room_Object, status_code=status.HTTP_201_CREATED)
async def add_Room(addRoom: Room_Object):
    db_classes = Room(room_id=addRoom.room_id,room_size=addRoom.room_size, measurement_unit=addRoom.measurement_unit)
    try:
        db_Session.add(db_classes)
        db_Session.flush()
        db_Session.commit()
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
    return addRoom

"""Returns all the rooms present in the database"""
@app.get("/Rooms", tags=["Rooms"],response_model=List[Room_Object], status_code=status.HTTP_200_OK)
async def get_AllRoom_Details():
    results = db_Session.query(Room).all()
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'No rooms are available')
    else: 
        return results

"""Returns a room with a certain room_id or an error if the room does not exist"""
@app.get("/Rooms/{room_id}",tags=["Rooms"],response_model=Room_Object, status_code=status.HTTP_200_OK)
async def get_Specific_Room(room_id: str):
    specificRoomDetail = db_Session.query(Room).filter(Room.room_id == room_id).first()
    if not specificRoomDetail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Room with the id {room_id} does not exist')
    else:
        return specificRoomDetail

""" Add number of people in room """
@app.post("/Rooms/{room_id}/PeopleInRoom",tags=["Rooms"], response_model=PeopleInRoomObject, status_code=status.HTTP_201_CREATED)
async def add_People_Room(room_id: str,addPeopleRoom: PeopleInRoomObject):
    db_classes = PeopleInRoom(room_id=room_id,people_count=addPeopleRoom.people_count)
    try:
        db_Session.add(db_classes)
        db_Session.flush()
        db_Session.commit()
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
    return addPeopleRoom

"""Returns people count in room"""
@app.get("/Rooms/{room_id}/PeopleInRoom",tags=["Rooms"],response_model=PeopleInRoomObject,status_code=status.HTTP_200_OK)
async def get_PeopleCount_Details(room_id: str):
    peoplecount = db_Session.query(PeopleInRoom).filter(PeopleInRoom.room_id==room_id).first()
    if not peoplecount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'people in Room with the id {room_id} does not exist')
    else:
        return peoplecount

"""Updates a room with a certain room_id or returns an error if the room does not exist"""
"""Example room update object 
   {
    "room_size": 55,
    "room_name": "Living room changed"
    }"""
   
@app.patch("/Rooms/{room_id}",tags=["Rooms"],response_model=Update_RoomObject,status_code=status.HTTP_200_OK)
async def update_RoomDetails(room_id: str, request: Update_RoomObject):
    updateRoomDetail = db_Session.query(Room).filter(Room.room_id == room_id).first()
    if not updateRoomDetail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Room with the id {room_id} is not available')
    room_data = request.dict(exclude_unset=True)
    for key, value in room_data.items():
            setattr(updateRoomDetail, key, value)
    db_Session.add(updateRoomDetail)
    db_Session.commit()
    db_Session.refresh(updateRoomDetail)    
    return updateRoomDetail

"""Deletes a room with a certain room_id or returns an error if the room does not exist"""
@app.delete("/Rooms/{room_id}",tags=["Rooms"], status_code=status.HTTP_200_OK)
async def delete_Room(room_id: str):
    deleteRoom = db_Session.query(Room).filter(Room.room_id == room_id).first()
    if not deleteRoom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Room with the room id {room_id} is not found')
    db_Session.delete(deleteRoom)
    db_Session.commit()
    return {"code": "success", "message": f"deleted room with id {room_id}"}

# Lights
"""Creates a new light in a room in the database and returns the light on success. Light_id needs to be unique in the room (Light_id is unique per definition due to zigbee)"""
"""Example light object 
{
    "light_id": "0x804b50fffeb72fd9",
    "name": "Led Strip"
}"""
@app.post("/Rooms/{room_id}/Lights", tags=["Lights"], response_model=Lights_Object, status_code=status.HTTP_201_CREATED)
async def add_light(room_id: str, addLight: Lights_Object):
    addLight = Light(room_id=room_id, light_id=addLight.light_id, name=addLight.name)
    try:
        db_Session.add(addLight)
        db_Session.flush()
        db_Session.commit()
        write_to_json("Lights", room_id, addLight.light_id)
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
    return addLight

"""Returns all the lights in a room"""
@app.get("/Rooms/{room_id}/Lights",tags=["Lights"], response_model=List[Lights_Object],status_code=status.HTTP_200_OK)
async def get_All_Lights(room_id: str):
    getAllLights = db_Session.query(Light).filter(Light.room_id == room_id).all()
    return getAllLights


"""Returns a specific light in a room or an error if the light does not exist in the room"""
@app.get("/Rooms/{room_id}/Lights/{light_id}/",tags=["Lights"], response_model=Lights_Object, status_code=status.HTTP_200_OK)
async def get_Specific_Light(room_id: str, light_id: str):
    getSpecificLight = db_Session.query(Light).filter(Light.room_id == room_id, Light.light_id == light_id).first()
    if not getSpecificLight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {light_id} is not available in room {room_id}')
    else:
     return getSpecificLight

"""Updates a specific light in a room and returns it or returns an error if the light does not exist in the room """
"""Example light object 
   {
    "name": "Led Strip changed"
    }"""
@app.patch("/Rooms/{room_id}/Lights/{light_id}",tags=["Lights"],response_model=Update_LightObject, status_code=status.HTTP_200_OK)
async def update_light(room_id: str, light_id: str, request: Update_LightObject):
    updateLight = db_Session.query(Light).filter(Light.room_id == room_id, Light.light_id == light_id).first()
    if not updateLight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {light_id} is not available in room {room_id}')
    light_data = request.dict(exclude_unset=True)
    for key, value in light_data.items():
            setattr(updateLight, key, value)
    db_Session.add(updateLight)
    db_Session.commit()
    db_Session.refresh(updateLight)   
    return updateLight

"""Deletes a specific light in a room or returns an error if the light does not exist in the room"""
@app.delete("/Rooms/{room_id}/Lights/{light_id}",tags=["Lights"], status_code=status.HTTP_200_OK)
async def delete_light(room_id: str, light_id: str):
    deleteLight = db_Session.query(Light).filter(Light.room_id == room_id, Light.light_id == light_id).first()
    if not deleteLight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {light_id} is not available in room {room_id}')
    db_Session.delete(deleteLight)
    db_Session.commit()
    delete_from_json(light_id)
    return {"code": "success", "message": f"deleted light with id {light_id} from room {room_id}"}

#  Lights Activation
"""Toggles a light in a room with a specific light_id"""
"""does not contain a body"""
@app.post("/Rooms/{room_id}/Lights/{light_id}/Activation",tags=["Lights"], status_code=status.HTTP_200_OK)
async def activate_Light(room_id: str, light_id: str,operation: Light_Activation_Object):
    data = {}
    #data["state"] = "TOGGLE"
    if operation.turnon == True:
        data["state"] = "ON"
    else:
        data["state"] = "OFF"
    topic = f"zigbee2mqtt/{light_id}/set"
    publish_message(topic, data)
    return {"code": "success", "message": "Device toggled"}

""" Get the details of when the light is turned on/off """
@app.get("/Rooms/{room_id}/Lights/{light_id}/Activation",tags=["Lights"],response_model=List[Light_Operation_Return_Object], status_code=status.HTTP_200_OK)
async def activate_Light(room_id: str, light_id: str):
    getLightDetails = db_Session.query(Light_Operation).filter(
        Light.room_id == room_id, Light.light_id == light_id).all()
    if not getLightDetails:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {light_id} is not available in room {room_id}')
    return getLightDetails

# Light set color
"""Changes the settings of a light via a Light Operation Objects."""
"""Example Light Operation Object 
   {
    "turnon": "ON",
    "brightness": 200,
    "color": {"hex":"#466bca"}
    }"""
@app.post("/Rooms/{room_id}/Lights/{light_id}/SetColor",tags=["Lights"],status_code=status.HTTP_200_OK)
async def complex_setting_light(room_id: str, light_id: str, operation: Light_Operation_Object):
    def isValidHexCode(str):
        if (str[0] != '#'):
            return False
        if (not(len(str) == 4 or len(str) == 7)):
            return False
        for i in range(1, len(str)):
            if (not((str[i] >= '0' and str[i] <= '9') or (str[i] >= 'a' and str[i] <= 'f') or (str[i] >= 'A' or str[i] <= 'F'))):
                return False
        return True
    data = {}
    color = {}
    if operation.turnon == True:
        data["state"] = "ON"
    else:
        data["state"] = "ON"

    if (isValidHexCode(operation.hex)):
        color["hex"] = operation.hex
    else:
        color["hex"]="#466bca"
    
    data["color"] = color
    data["brightness"] = operation.brightness
    topic = f"zigbee2mqtt/{light_id}/set"
    publish_message(topic, data)
    
    return {"code": "success", "message": "Device Settings changed"}

# Ventilators
"""Creates a new power plug for ventilator in a room in the database and returns the power plug on success. Plug_id needs to be unique in the room (Sensor_id is unique per definition due to zigbee)"""
"""Ventilators attached to smart power plug to turn or off"""
"""Example Power Plug object 
   {
    "plug_id": "0x804b50fffeb72fd9",
    "name": "Plug 1"
    }"""
@app.post("/Rooms/{room_id}/Ventilators",tags=["Ventilators"], response_model=Power_Plug_Object,status_code=status.HTTP_201_CREATED)
async def add_Power_Plug(room_id: str, addPowerPlug: Power_Plug_Object):
    addPowerPlug = Power_Plug(room_id=room_id, plug_id=addPowerPlug.plug_id, name=addPowerPlug.name)
    try:
        db_Session.add(addPowerPlug)
        db_Session.flush()
        db_Session.commit()
        write_to_json("Ventilators", room_id, addPowerPlug.plug_id)
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
    return addPowerPlug

"""Returns all the power plug in a room"""
@app.get("/Rooms/{room_id}/Ventilators",tags=["Ventilators"], response_model=List[Power_Plug_Object], status_code=status.HTTP_200_OK)
async def get_All_Power_Plugs(room_id: str):
    allPowerPlugs = db_Session.query(Power_Plug).filter(Power_Plug.room_id == room_id).all()
    return allPowerPlugs

"""Returns a specific power plug in a room or an error if the power plug does not exist in the room"""
@app.get("/Rooms/{room_id}/Ventilators/{plug_id}", tags=["Ventilators"],response_model=Power_Plug_Object, status_code=status.HTTP_200_OK)
async def get_Specific_Light(room_id: str, plug_id: str):
    getSpecificPowerPlug = db_Session.query(Power_Plug).filter(
        Power_Plug.room_id == room_id, Power_Plug.plug_id == plug_id).first()
    if not getSpecificPowerPlug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Power Plug with the id {plug_id} is not available in room {room_id}')
    else:
     return getSpecificPowerPlug

"""Updates a specific power plug in a room and returns it or returns an error if the power plug does not exist in the room """
"""Example Power Plug update object 
{
    "name": "Plug 1 changed"
}"""
@app.patch("/Rooms/{room_id}/Ventilators/{plug_id}",tags=["Ventilators"], response_model=Power_Plug_Object, status_code=status.HTTP_200_OK)
async def update_power_plug(room_id: str, plug_id: str, request: Power_Plug_Update_Object):
    
    updatePowerPlug = db_Session.query(Power_Plug).filter(
        Power_Plug.room_id == room_id, Power_Plug.plug_id == plug_id).first()
        
    if not updatePowerPlug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Plug with the id {plug_id} is not available in room {room_id}')
    plug_data = request.dict(exclude_unset=True)
    for key, value in plug_data.items():
            setattr(updatePowerPlug, key, value)
    db_Session.add(updatePowerPlug)
    db_Session.commit()
    db_Session.refresh(updatePowerPlug) 
    return updatePowerPlug

"""Deletes a specific power plug  in a room or returns an error if the power plug does not exist in the room"""
@app.delete("/Rooms/{room_id}/Ventilators/{plug_id}",tags=["Ventilators"], status_code=status.HTTP_200_OK)
async def delete_power_plug(room_id: str, plug_id: str):
    
    deletePowerPlug = db_Session.query(Power_Plug).filter(
        Power_Plug.room_id == room_id, Power_Plug.plug_id == plug_id).first()
        
    if not deletePowerPlug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {plug_id} is not available in room {room_id}')
    db_Session.delete(deletePowerPlug)
    db_Session.commit()
    delete_from_json(plug_id)
    return {"code": "success", "message": f"deleted ventilator with id {plug_id} from room {room_id}"}

# Ventilators Operations

"""Post Operational Data for a power plug in a room"""
"""Example Operational Power Plug object 
    {
        "turnon": True
    }""" 

"""Toggles a power plug(ventilator) in a room with a specific plug_id"""
"""does not contain a body"""
"""
@app.post("/Rooms/{room_id}/Ventilators/{plug_id}/Operations",tags=["Ventilators"],status_code=status.HTTP_200_OK)
async def activate_Power_Plug(room_id: str, plug_id: str,body: Power_Plug_Storing_Object):
   
    new_operation = Power_Plug_Operation(room_id=room_id, plug_id=plug_id, time=datetime.now(), turnon = body.turnon)
   
    last_operation = db_Session.query(Power_Plug_Operation).filter(Power_Plug_Operation.room_id == room_id, Power_Plug_Operation.plug_id == plug_id).order_by(Power_Plug_Operation.time.desc()).first()

    #Lupus 12133 plugs are not completely compatible with zigbee2mqtt and tend to send multiple state events --> this ensures to only store one of the event states
    if last_operation == None or (last_operation != None and last_operation.turnon != new_operation.turnon):
        try:
            db_Session.add(new_operation)
            db_Session.flush()
            db_Session.commit()
        except Exception as ex:
            logger.error(f"{ex.__class__.__name__}: {ex}")
            db_Session.rollback()
    return new_operation
"""
"""Toggles a power plug in a room with a specific plug_id"""
"""does not contain a body"""
@app.post("/Rooms/{room_id}/Ventilators/{plug_id}/Activation", tags=["Ventilators"],status_code=status.HTTP_200_OK)
async def activate_Power_Plug(room_id: str, plug_id: str):

    data = {}
    data["state"] = "TOGGLE"
    topic = f"zigbee2mqtt/{plug_id}/set"

    publish_message(topic, data)

    return {"code": "success", "message": "Device toggled"}
""" Get the details of when the Ventilator is turned on/off """
@app.get("/Rooms/{room_id}/Ventilators/{plug_id}/Activation",tags=["Ventilators"],response_model=List[Power_Plug_Operation_Object],status_code=status.HTTP_200_OK)
async def ventilator_Details(room_id: str, plug_id: str):
    getVentilatorDetails = db_Session.query(Power_Plug_Operation).filter(
        Power_Plug.room_id == room_id, Power_Plug.plug_id == plug_id).all()
    if not getVentilatorDetails:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Ventilator with the id {plug_id} is not available in room {room_id}')
    return getVentilatorDetails

#**Helper Methods**

"""Writes to devices.json after a new device is saved in the database"""
def write_to_json(device_type, device_room, device_key):
     with open("devices.json", 'r+') as f:
        devices = json.load(f)
        information = {}
        information["device_type"] = device_type
        information["device_room"] = device_room
        devices[device_key] = information
        f.seek(0)
        json.dump(devices, f, indent = 4)

"""Deletes a device from the device.json file once a device is deleted from the database"""
def delete_from_json(device_key):
    with open("devices.json", 'r+') as f:
        devices = json.load(f)
        f.truncate(0)
        del devices[device_key]
        f.seek(0)
        json.dump(devices, f, indent = 4)

#Air Quality APIs - airQualityinRoom

@app.post("/Room/AirQuality/",tags=["AirQuality"], response_model=AirQuality_Properties_Object,status_code = status.HTTP_201_CREATED)
async def add_AirQuality_Properties(addAirQuality:AirQuality_Properties_Object):
   
    db_AQP=Airqualityproperty(room_id=addAirQuality.room_id,device_id=addAirQuality.device_id,ventilator=addAirQuality.ventilator,co2=addAirQuality.co2,co2measurementunit=addAirQuality.co2measurementunit,temperature=addAirQuality.temperature,temperaturemeasurementunit=addAirQuality.temperaturemeasurementunit,humidity=addAirQuality.humidity,humiditymeasurementunit=addAirQuality.humiditymeasurementunit,time=addAirQuality.time)
     
    try:
        db_Session.add(db_AQP)
        db_Session.flush()
        db_Session.commit()
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
    return addAirQuality

@app.get("/Room/{room_id}/AirQuality/",tags=["AirQuality"], response_model=Page[AirQuality_Properties_Object], status_code = status.HTTP_200_OK)
async def get_AirQuality_Rooms(room_id:str):
    filteredAQPResults= db_Session.query(Airqualityproperty).filter(Airqualityproperty.room_id==room_id)
    AQPresults=filteredAQPResults.all()
    if not AQPresults:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'No air quality measurements available for the room {room_id}')
    else:
        return paginate(AQPresults)
    
@app.get("/Room/{room_id}/AirQuality/temperature/",tags=["AirQuality"], response_model=Page[AirQuality_Temperature_Object], status_code = status.HTTP_200_OK)
async def get_AirQuality_Temperature(room_id:str):
    filteredAQTResults= db_Session.query(Airqualityproperty).filter(Airqualityproperty.room_id==room_id)
    AQPTemperature=filteredAQTResults.all()
    if not AQPTemperature:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'No temperature data available for room id {room_id}')
    else:
        return paginate(AQPTemperature)


@app.get("/Room/{room_id}/AirQuality/humidity/",tags=["AirQuality"], response_model=Page[AirQuality_Humidity_Object], status_code = status.HTTP_200_OK)
async def get_AirQuality_Humidity(room_id:str):
    filteredAQHResults=db_Session.query(Airqualityproperty).filter(Airqualityproperty.room_id==room_id)
    AQPHumidity=filteredAQHResults.all()
    if not AQPHumidity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'No humidity data available for room id {room_id}')
    else:
        return paginate(AQPHumidity)

@app.get("/Room/{room_id}/AirQuality/co2/",tags=["AirQuality"], response_model=Page[AirQuality_Co2_Object], status_code = status.HTTP_200_OK)
async def get_AirQuality_Co2(room_id:str):
    filteredAQCo2Results=db_Session.query(Airqualityproperty).filter(Airqualityproperty.room_id==room_id)
    AQPCo2=filteredAQCo2Results.all()
    if not AQPCo2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'No co2 data available for room id {room_id}')
    else:
     return paginate(AQPCo2)      

# Doors
@app.post("/Rooms/{room_id}/Doors/", tags=["Doors"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def add_Door():
    return {"HTTP_501_NOT_IMPLEMENTED"}
@app.get("/Rooms/{room_id}/Doors/",tags=["Doors"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_Door():
    getDoor=status.HTTP_501_NOT_IMPLEMENTED
    return getDoor
@app.get("/Rooms/{room_id}/Doors/{door_id}",tags=["Doors"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_SpecificDoor():
    getSpecificDoor=status.HTTP_501_NOT_IMPLEMENTED
    return getSpecificDoor
@app.put("/Rooms/{room_id}/Doors/{door_id}",tags=["Doors"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def update_SpecificDoor():
    updateSpecificDoor=status.HTTP_501_NOT_IMPLEMENTED
    return updateSpecificDoor
@app.post("/Rooms/{room_id}/Doors/{door_id}/Open",tags=["Doors"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def open_Door():
    openSpecificDoor=status.HTTP_501_NOT_IMPLEMENTED
    return openSpecificDoor
@app.get("/Rooms/{room_id}/Doors/{door_id}/Open",tags=["Doors"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def getOpen_Door():
    detailDoorOperation=status.HTTP_501_NOT_IMPLEMENTED
    return detailDoorOperation

# Windows
@app.post("/Rooms/{room_id}/Windows/", tags=["Windows"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def add_Window():
    addWindow=status.HTTP_501_NOT_IMPLEMENTED
    return addWindow
@app.get("/Rooms/{room_id}/Windows/",tags=["Windows"],  status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_Window():
    getWindow=status.HTTP_501_NOT_IMPLEMENTED
    return getWindow
@app.get("/Rooms/{room_id}/Windows/{window_id}",tags=["Windows"],  status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_SpecificWindow():
    getSpecificWindow=status.HTTP_501_NOT_IMPLEMENTED
    return getSpecificWindow
@app.put("/Rooms/{room_id}/Windows/{window_id}",tags=["Windows"],  status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def update_SpecificWindow():
    UpdateSpecificWindow=status.HTTP_501_NOT_IMPLEMENTED
    return UpdateSpecificWindow
@app.post("/Rooms/{room_id}/Windows/{window_id}/Open", tags=["Windows"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def open_Window():
    openSpecificWindow=status.HTTP_501_NOT_IMPLEMENTED
    return openSpecificWindow
@app.get("/Rooms/{room_id}/Windows/{window_id}/Open",tags=["Windows"],  status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def getOpen_Window():
    detailWindowOperation=status.HTTP_501_NOT_IMPLEMENTED
    return detailWindowOperation
