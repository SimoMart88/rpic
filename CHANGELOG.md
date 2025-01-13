## 0.2.0 (2025-01-11)

### Feat

- **gpio**: implement db lock on DHT22 sensor read
- **install**: migrate db from sqlite to postgresql
- **Device**: implement support to store status
- **uwsgi**: implement support for uwsgi
- **HomePageView**: implement very basic home page UI with bootstrap5
- **Admin**: implement support for test button in Sensor admin UI
- **DeviceAdmin**: implement configure ui
- **Dht22SensorInterface**: implement SensorInterface for DHT22 component
- **core**: move core package content under rpi_controller
- **Sensor**: implement Sensor model
- **Device**: implement Device model
- **rpi_controller**: implement django project for rpi_controller

### Fix

- **gpio**: move implementation from adafruit-circuitpython-dht to pigpio
- **Sensor**: fix interface registry definition

### Refactor

- **install**: update install script configuration
- **uv.lock**: move django-stubs from dev dependencies to main
- **install**: fix wrong executable path definition in the install script
- **admin**: implement proper django-stubs-ext support for DeviceAdmin
- **admin**: implement Admin configuration for Sensor model
- **Dht22SensorInterface**: include config_form and template_name configurations
- **Interface**: improve Interface class attribute names
- **Sensor**: remove gpio config
- **InterfaceRegistry**: implement InterfaceRegistry class
