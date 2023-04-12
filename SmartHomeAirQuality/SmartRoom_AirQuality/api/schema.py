# coding: utf-8
from sqlalchemy import Boolean, Column, Float, DateTime, ForeignKey, Integer, String, Table, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class UserDetails(Base):
    __tablename__ = "user_details"

    username = Column(String, primary_key=True)
    user_password = Column(String)
    
class DigitalTwins(Base):
    __tablename__ = "digital_twins"
    
    dt_id = Column(String, primary_key=True)
    dt_type = Column(String, nullable=False)
    dt_location=Column(String, nullable=False)
    dt_active_status=Column(Boolean, nullable=False)
    dt_capability=Column(String, nullable=False)
    
class Room(Base):
    __tablename__ = 'room'

    room_id = Column(ForeignKey('digital_twins.dt_id'), primary_key=True)
    room_size = Column(Integer, nullable=False)
    measurement_unit = Column(String, nullable=False)

class PeopleInRoom(Base):
    __tablename__ = 'peopleinroom'
    room_id = Column(ForeignKey('digital_twins.dt_id'), primary_key=True)
    people_count = Column(Integer, primary_key = True)
	
    digital_twins = relationship('DigitalTwins')

class Light(Base):
    __tablename__ = 'light'

    room_id = Column(ForeignKey('digital_twins.dt_id'), primary_key=True)
    light_id = Column(String, primary_key = True)
    name = Column(String, nullable=False) 
    
    digital_twins = relationship('DigitalTwins')

class Light_Operation(Base):
    __tablename__ = "light_operation"

    light_id = Column(String, primary_key=True)
    room_id = Column(String, nullable=False)
    time = Column(DateTime, primary_key=True)
    turnon = Column(Boolean, nullable=False)
    hex=Column(String,nullable=False)
    brightness = Column(Integer, nullable=False)

    __table_args__ = (ForeignKeyConstraint([light_id, room_id], [Light.light_id, Light.room_id]), {})

    light = relationship('Light')
    


class Power_Plug(Base):
    __tablename__ = 'power_plug'

    room_id = Column(ForeignKey('digital_twins.dt_id'), primary_key=True)
    plug_id = Column(String, primary_key=True)
    name = Column(String, nullable = False)

    digital_twins = relationship('DigitalTwins')

class Power_Plug_Operation(Base):
    __tablename__ = "power_plug_operation"

    plug_id = Column(String, primary_key=True)
    room_id = Column(String, nullable=False)
    time = Column(DateTime, primary_key=True)
    turnon = Column(Boolean, nullable=False)

    __table_args__ = (ForeignKeyConstraint([plug_id, room_id], [Power_Plug.plug_id, Power_Plug.room_id]), {})

    power_plug = relationship('Power_Plug')


class Airqualityproperty(Base):
    __tablename__ = 'airqualityproperties'

    room_id = Column(ForeignKey('digital_twins.dt_id'), nullable=False)
    device_id = Column(String, nullable=False)
    ventilator = Column(String, nullable=False)
    co2 = Column(Float(53), nullable=False)
    co2measurementunit = Column(String, nullable=False)
    temperature = Column(Float(53), nullable=False)
    temperaturemeasurementunit = Column(String, nullable=False)
    humidity = Column(Float(53), nullable=False)
    humiditymeasurementunit = Column(String, nullable=False)
    time = Column(DateTime, primary_key=True)

    digital_twins = relationship('DigitalTwins')