# rpi-controller

[![Test](https://github.com/SimoMart88/rpi-controller/actions/workflows/test.yml/badge.svg)](https://github.com/SimoMart88/rpi-controller/actions/workflows/test.yml)

A controller for GPIO sensors and devices on RaspberryPI

## Compatibility
- Tested on RaspberryPi 1b
  - OS: Raspberry Pi OS (Legacy) Lite (see https://www.raspberrypi.com/software/operating-systems/)

## Installation
- Download release file into the target RaspberryPI
- Unzip the file into a temp folder
- Run `sudo ./install` inside the temp folder
- During the first installation, automatically generated passwords (Postgresql, Django Admin, etc...) will be prompted
  - If you miss it, we can find it in /opt/rpic/app/.env

# Future improvements
## Documentation
* Implement HLA

## Features
* Use a qualified relationship to link Controller with Sensors and Actuators to include labels
  * Validate this relationship against interface on form save
* Implement scheduler for recurrent operations (Celery)
* Implement a telemetry system to track device status changes in time
* Implement support for LoRa based devices

## Refactoring
# Move common logic from concrete models (Sensor/Actuator/Controller) to the abstract model (Device)

## Security
* Protect UI and API with authentication and authorization mechanism

## Infrastructure
* Expose the application and the static content through Nginx
  * For small environment uWSGI could be enough, for medium to large environment Nginx would be better

## Installer
* Run installation and application with a dedicated user
  * Improve security
