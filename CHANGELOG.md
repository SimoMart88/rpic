## 0.13.0 (2025-08-05)

### Feat

- **lock_db_record**: implement decorator to lock at db record level when a operation is performed on GPIO
- **Relay**: implement ARM64 compatibility support
- **DHT22**: implement ARM64 compatibility support
- **Admin**: configured permissions for extra buttons and views

### Fix

- **SensorTemperatureStepScaleFanControllerForm**: fix secondary_fan_actuator field initial value config
- **Relay**: is_active now support expected value
- **create_hardware_interface**: implement proper use of importlib.util.find_spec
- **pyproject.toml**: fixed adafruit and lgpio architecture import based

## 0.12.0 (2025-07-08)

### Feat

- **install**: include ENVIRONMENT and SENTRY_DNS config support
- **Home**: include footer with version
- **views**: move module into the web package
- **Sentry**: implement support with Django and Celery integration enabled

### Fix

- **install**: implement proper default value management

## 0.11.0 (2025-07-01)

### Feat

- **RelayActuatorInterface**: implement support for contacts state (NO/NC)

## 0.10.0 (2025-06-30)

### Feat

- **Home**: implement read_status support for Actuators
- **ActuatorViewSet**: implement read_status support
- **Actuator**: implement read_status support
- **RelayActuatorInterface**: implement read_input support

## 0.9.1 (2025-06-25)

### Fix

- **SensorTemperatureStepScaleFanControllerInterface**: fix fans visualization on UI
- **SensorTemperatureStepScaleFanControllerInterface**: round delta temperature

## 0.9.0 (2025-06-25)

### Feat

- **SensorTemperatureStepScaleFanControllerInterface**: include temperature delta in status

## 0.8.1 (2025-06-25)

### Fix

- **RelayActuatorInterface**: call GPIO.cleanup at the end of every operation

## 0.8.0 (2025-06-25)

### Feat

- **Dht22SensorInterface**: move from pigpio to RPI_Adafruit_Python_DHT

### Fix

- **install**: remove pigpiod dependency

## 0.7.0 (2025-06-23)

### Feat

- **Install**: perform InfluxDB installation and application configuration on target system
- **Admin**: implement monitor view support for Devices
- **system_monitor_update_handler**: implement post Device update handler to track changes with SystemMonitor
- **post_device_control**: implement post control operation signal for Device models
- **system_monitor_setup**: implement Django command to run SystemMonitor setup
- **SystemMonitorHandler**: implement BaseConnectionHandler and ConnectionProxy for SystemMonitor
- **SystemMonitor**: implement base class and InfluxDB monitoring backends

## 0.6.2 (2025-05-28)

### Fix

- **Admin**: set correct periodic_task_name in ControllerAdmin

## 0.6.1 (2025-05-28)

### Fix

- **SensorTemperatureStepScaleFanControllerForm**: fix initial data override problem
- **GPIO**: fixed typo error in form help text

### Refactor

- **SensorTemperatureStepScaleFanControllerInterface**: fixed wrong information log

## 0.6.0 (2025-05-27)

### Feat

- **Install**: update install script to include Redis and Celery support
- **Admin**: improve Crontab expression input in Admin UI using Cronstrue
- **Admin**: implement simplified PeriodicTask configuration UI
- **Tasks**: implement support for Controller update_status async execution
- **Tasks**: implement support for Actuator update_status async execution
- **Tasks**: implement support for Sensor read_status async execution
- **Celery**: Implement Celery support

## 0.5.0 (2025-05-07)

### Feat

- **Controller**: implement UI support
- **Controller**: implement API support for status update
- **SensorTemperatureStepScaleFanControllerInterface**: implement SensorTemperatureStepScaleFanControllerInterface logic
- **Controller**: implement support for Controller model

### Refactor

- **Device**: move interface controll logic to a common method

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
