from sqlite3 import Timestamp
from xmlrpc.client import DateTime
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union

class Token(BaseModel):
    access_token: str
    token_type: str

class UserAuthenticate(BaseModel):
    username: str
    password: str

class UserInfoBase(BaseModel):
    username: str
    class Config:
        orm_mode = True
        
class UserCreate(UserInfoBase):
    password: str

#DTs
class DigitalTwin_Object(BaseModel):
    dt_id:str
    dt_type: str 
    dt_location:str
    dt_active_status:bool
    dt_capability:str  
    class Config:
        orm_mode = True
      
#Smart_Room
class Room_Object(BaseModel):
    room_id: str
    room_size:int
    measurement_unit:str
    class Config:
        orm_mode = True

class PeopleInRoomObject(BaseModel):
    room_id:str
    people_count:int
    class Config:
        orm_mode = True

class Update_RoomObject(BaseModel):
    room_size:Optional[int]=None
    measurement_unit:Optional[str]=None
    class Config:
        orm_mode = True

class Lights_Object(BaseModel):
    light_id: str
    name: str
    class Config:
        orm_mode = True

class Update_LightObject(BaseModel):
    name: Optional[str]=None
    class Config:
        orm_mode = True

class Light_Activation_Object(BaseModel):
    turnon:bool
    class Config:
        orm_mode = True
        
class Light_Operation_Object(BaseModel):
    turnon:bool
    brightness: int
    hex: str
    class Config:
        orm_mode = True        

class Light_Operation_Storing_Object(BaseModel):
    turnon:bool
    brightness: int
    hex: str
    class Config:
        orm_mode = True  

class Light_Operation_Return_Object(BaseModel):
    turnon:bool
    brightness: int
    hex: str
    time: Timestamp
    class Config:
        orm_mode = True


class Time_Query_Object(BaseModel):
    interval: int
    timespan_from: int
    timespan_to: int
    

class Power_Plug_Object(BaseModel):
    plug_id: str
    name: str
    class Config:
        orm_mode = True

class Power_Plug_Operation_Object(BaseModel):
    turnon: bool
    time: Timestamp
    class Config:
        orm_mode = True

class Power_Plug_Update_Object(BaseModel):
    name: str
    class Config:
        orm_mode = True

class Power_Plug_Storing_Object(BaseModel):
    turnon:bool
    class Config:
        orm_mode = True

#Air Quality
 
class AirQuality_Properties_Object(BaseModel):
    room_id: str
    device_id:str
    ventilator:str
    co2:float
    co2measurementunit:str
    temperature:float
    temperaturemeasurementunit:str
    humidity:float
    humiditymeasurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True

class AirQuality_Temperature_Object(BaseModel):
    room_id: str
    ventilator:str
    temperature:int
    temperaturemeasurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True

class AirQuality_Humidity_Object(BaseModel):
    room_id: str
    ventilator:str
    humidity:int
    humiditymeasurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True     

class AirQuality_Co2_Object(BaseModel):
    room_id: str
    ventilator:str
    co2:int
    co2measurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True             


