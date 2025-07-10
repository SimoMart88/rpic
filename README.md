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

### Notes
- For InfluxDB default credential will be used, change it if your RaspberryPi is exposed on internet

# Future improvements
## Documentation
### Mandatory for v1
* Implement HLA
* Document how to customize the installation process

### Future
* Document how to contribute
* Document how to extend the system

## Features
### Mandatory for v1
* Improve code coverage

### Future
* Implement a caching system for API calls
  * Improving performance by reducing DB access
* Implement System Monitor data export in the Admin UI
* Implement UI with graphs support for System Monitor
* Implement support for LoRa based devices
* Implement support for PWA (https://github.com/silviolleite/django-pwa)

## Security
### Mandatory for v1
* Apply permission control on Admin buttons and views
* Apply Bandit (https://bandit.readthedocs.io/en/latest/) security scan

### Future
* Protect UI and API with authentication and an authorization mechanism

## Infrastructure
### Future
* Expose the application and the static content through Nginx
  * For a small environment uWSGI could be enough, for medium to large environment Nginx would be better

## Installer
### Mandatory for v1
* Run installation and application with a dedicated user
  * Improve security
* Implement check command extension to include required env variables

### Future
* Move installer to a dedicated Python(click) script
  * Better parameter management

# Known issues
