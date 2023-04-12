# pull official base image
FROM python:3.9.6-alpine

COPY ./requirements.txt /app/requirements.txt

# set work directory
WORKDIR /app
COPY ./SmartRoom_AirQuality/api ./app
RUN apk add --no-cache gcc musl-dev build-base postgresql-dev libffi-dev
RUN pip install -r requirements.txt

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000 1884