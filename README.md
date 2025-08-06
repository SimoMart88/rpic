# rpi-controller

[![Test](https://github.com/SimoMart88/rpi-controller/actions/workflows/test.yml/badge.svg)](https://github.com/SimoMart88/rpi-controller/actions/workflows/test.yml)

A simple and extensible controller for GPIO sensors and devices on RaspberryPI

## Compatibility
- Tested on
  - RaspberryPi 1b
    - OS: Raspberry Pi OS (Legacy) Lite
    - Postgres: 13.18
    - Redis: 6.0.16
    - InfluxDB: 1.6.7
  - RaspberryPi 5
    - OS: Raspberry Pi OS (64-bit) Lite
    - Postgres: 17.5
    - Redis: 8.0.3
    - InfluxDB: 1.11

## Installation
- Download release file into the target RaspberryPI
- Unzip the file into a temp folder
- Run `sudo ./install` inside the temp folder
- During the first installation, automatically generated passwords (Postgresql, Django Admin, etc...) will be prompted
  - If you miss it, we can find it in /opt/rpic/app/.env

### Notes
- For InfluxDB default credential will be used, change it if your RaspberryPi is exposed on internet

# Roadmap
## Documentation
### Mandatory for v1
* Document HLA
* Document how to use the application
* Document how to contribute
* Document how to extend the system

## Features
### Future
* Implement a caching system for API calls
  * Improving performance by reducing DB access
* Implement System Monitor data export in the Admin UI
* Implement UI with graphs support for System Monitor
* Implement support for LoRa based devices
* Implement support for PWA (https://github.com/silviolleite/django-pwa)

## Security
### Future
* Protect UI and API with authentication and an authorization mechanism

## Infrastructure
### Future
* Expose the application and the static content through Nginx
  * For a small environment uWSGI could be enough, for medium to large environment Nginx would be better

## Installer
### Mandatory for v1
* Remove external system dependencies (postgres, redis, etc...) installation and configuration from the installer
  * Document how to install and configure the external system dependencies
  * Document how to customize the installation process
* Run installation and application with a dedicated user to improve security
* Implement check command extension to include required env variables

### Future
* Move installer to a dedicated Python(click) script
  * Better parameter management
* Move installer to docker compose

# Known issues
* None for now
