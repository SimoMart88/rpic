## 0.4.2 (2025-03-28)

### Fix

- **utils.js**: fix empty data management in read_device_status function

## 0.4.1 (2025-03-27)

### Fix

- **RelayActuator**: fix missing JQuery ID reference in relay template
- **RelayActuatorInterface**: fixed RPi.GPIO import problem by moving import to a local method
- **RelayActuatorInterface**: include debug logs

## 0.4.0 (2025-03-07)

### Feat

- **DeviceException**: implement custom exceptions for Device models
- **Home**: implement support for Actuators in home page
- **Actuator**: implement API
- **Device**: use method has been replaced by read_status and update_status
- **ActuatorInterface**: Implement support for relay and mock actuators
- **Admin**: Implement support for Actuator in Admin console
- **Actuator**: Implement support for Actuators as Django model

### Fix

- **Device**: rename last_status_update attribute to last_status_update_time to avoid confusion with last_update_status
- **Model**: restored Device as an abstract model

## 0.3.0 (2025-02-06)

### Feat

- **utils.js**: Move JavaScript code from the Homepage into a dedicate JavaScript file
- **Home**: implement async status update
- **api**: implement API for Sensor model
- **settings**: implement logging support

### Fix

- **HomePage**: Fix NavBar on mobile
- **Device**: implement support for "no update" operation using exceptions
- **gpio**: DHT22 now properly return update_last_status_datetime key when status update is not required
- **gpio**: fix DHT22 refresh_min_interval to avoid too frequent reads on the sensor

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
