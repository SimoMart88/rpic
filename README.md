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
* Implement a monitoring system to track devices status changes in time
* Integrate Sentry (https://sentry.io/)
  * Better runtime error management
* Move installer to a dedicated Python(click) script
  * Better parameter management
  * https://unix.stackexchange.com/questions/228277/grouping-systemd-services
* Implement support for LoRa based devices
* Implement caching system for API calls
  * Improve performance reducing DB access

## Refactoring

## Security
* Apply Bandit (https://bandit.readthedocs.io/en/latest/) security scan
* Apply permission control on Admin buttons and views
* Protect UI and API with authentication and authorization mechanism

## Infrastructure
* Expose the application and the static content through Nginx
  * For small environment uWSGI could be enough, for medium to large environment Nginx would be better

## Installer
* Run installation and application with a dedicated user
  * Improve security

# Known issues
* SensorTemperatureStepScaleFanControllerForm does not load delta_temperature_step and cooldown_period fields value on configuration edit
* SensorTemperatureStepScaleFanController core logic fails on temperature delta
* pgpio solution for DHT sensor is very fragile
  * Evaluate a more robust solution
    * Make https://github.com/adafruit/Adafruit_Python_DHT/ compatible with Uv?
