CREATE TABLE User_Details(
	username varchar PRIMARY KEY NOT NULL,
	user_password varchar NOT NULL
);
CREATE TABLE Digital_Twins(
	dt_id varchar PRIMARY KEY NOT NULL,
	dt_type varchar NOT NULL,
	dt_location varchar NOT NULL,
	dt_active_status BOOLEAN NOT NULL,
    dt_capability varchar NOT NULL
);
CREATE TABLE Room(
	room_Id varchar NOT NULL,
	room_Size int NOT NULL,
	measurement_Unit varchar NOT NULL,
	PRIMARY KEY (room_Id, room_Size),
	FOREIGN KEY (room_Id) REFERENCES Digital_Twins (dt_id)
);

CREATE TABLE PeopleInRoom(
	room_Id varchar NOT NULL,
    people_count int NOT NULL,
	PRIMARY KEY (room_Id, people_count),
	FOREIGN KEY (room_Id) REFERENCES Digital_Twins (dt_id)
);

CREATE TABLE AirQualityProperties(
	room_Id varchar  NOT NULL,
    device_id varchar  NOT NULL,
	ventilator varchar NOT NULL,
	co2 float NOT NULL,
	co2MeasurementUnit varchar NOT NULL,
	temperature float NOT NULL,
	temperatureMeasurementUnit varchar NOT NULL,
	humidity float NOT NULL,
	humidityMeasurementUnit varchar NOT NULL,
	time timestamp with time zone PRIMARY KEY NOT NULL,
	FOREIGN KEY (room_Id) REFERENCES Digital_Twins (dt_id)
);

CREATE TABLE Light(
	room_id varchar NOT NULL,
	light_id varchar NOT NULL,
	name varchar NOT NULL,
	PRIMARY KEY (room_id, light_id),
	FOREIGN KEY (room_id) REFERENCES Digital_Twins (dt_id)
	ON DELETE CASCADE
);

CREATE TABLE Light_Operation(
	light_id varchar NOT NULL,
	room_id varchar NOT NULL,
	time timestamp NOT NULL,
	turnon BOOLEAN NOT NULL,
	color_x DECIMAL NOT NULL,
	color_y DECIMAL NOT NULL,
	brightness INTEGER NOT NULL,
	PRIMARY KEY (light_id, time),
	FOREIGN KEY (room_id, light_id) REFERENCES Light (room_id, light_id)
	ON DELETE CASCADE
);

SELECT create_hypertable('Light_Operation', 'time');
CREATE INDEX ix_light_id_room_id_time ON Light_Operation (light_id, room_id, time DESC);


CREATE TABLE Power_Plug(
	room_Id varchar NOT NULL,
	plug_Id varchar NOT NULL,
	name varchar NOT NULL,
	PRIMARY KEY (room_Id, plug_Id),
	FOREIGN KEY (room_Id) REFERENCES Digital_Twins (dt_id)
	ON DELETE CASCADE
);

CREATE TABLE Power_Plug_Operation(
	plug_id varchar NOT NULL,
	room_id varchar NOT NULL,
	time timestamp NOT NULL,
	turnon BOOLEAN NOT NULL,
	PRIMARY KEY (plug_id, time),
	FOREIGN KEY (room_id, plug_id) REFERENCES Power_Plug (room_id, plug_id)
	ON DELETE CASCADE
);

SELECT create_hypertable('Power_Plug_Operation', 'time');
CREATE INDEX ix_plug_id_room_id_time ON Power_Plug_Operation (plug_id, room_id, time DESC);
