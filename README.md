# rpi-controller
A controller for GPIO sensors and devices on RaspberryPI

## Compatibility
- Tested on RaspberryPi 1b+ (https://www.raspberrypi.com/products/raspberry-pi-1-model-b-plus/)
  - OS: Raspberry Pi OS (Legacy) Lite (see https://www.raspberrypi.com/software/operating-systems/)

## Installation
- Download release file into the target RaspberryPI
- Unzip the file into a temp folder
- Run `sudo ./install` inside the temp folder
- During the first installation, automatically generated passwords (Postgresql, Django Admin, etc...) will be prompted
  - If you miss it, we can find it in the /opt/rpic/app/.env

# Future improvements
* Expose the application and the static content through Nginx
  * For small environment uWSGI could be enough, for medium to large environment Nginx would be better
* Run installation and application with a dedicated user
  * Improve security

# TODO
* Implement HLA
