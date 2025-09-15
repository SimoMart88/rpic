# RaspberryPi Controller

[![Test](https://github.com/SimoMart88/rpi-controller/actions/workflows/test.yml/badge.svg)](https://github.com/SimoMart88/rpi-controller/actions/workflows/test.yml)

A simple and extensible controller for GPIO sensors and actuators on RaspberryPI with web-based management and automation capabilities.

![HLA](docs/HLA.drawio.png)

## Overview
The main dashboard displays real-time data from connected GPIO sensors and actuators, providing instant status updates and control options through an intuitive web interface.
![Dashboard Overview](docs/overview/Landing.png)

The admin interface enables easy configuration and management of GPIO devices, allowing users to set up devices, define parameters, and monitor the status.
![Device Management](docs/overview/DeviceUpdate.png)

Flexible GPIO pin configuration system lets users assign and customize pin settings, and communication parameters for various sensor and actuators types.
![GPIO Configuration](docs/overview/DeviceConfig.png)

Built-in scheduling system provides automated task execution and periodic device monitoring, enabling hands-free operation and reliable system maintenance.
![Task Automation](docs/overview/DeviceSchedule.png)

## Real-World Use Case: Automated Cabinet Cooling System

I used this application to create an intelligent temperature-controlled ventilation system for equipment cabinet that require temperature regulation.

### Problem
Electronic equipment housed in cabinets or enclosures often generates heat that needs to be managed.
Simple always-on fans waste energy and create unnecessary noise, while no ventilation can lead to overheating and equipment failure.

### Solution
Using this application with sensors and relays, I created an automated cooling system that:

- **Monitors** inside and outside cabinet temperatures using DHT22 sensors
- **Calculates** the temperature differential between environments
- **Controls** exhaust/intake fans via relay switches based on intelligent logic
- **Optimizes** energy usage by only running fans when beneficial

### Hardware Setup
- **Inside sensor**: DHT22 temperature/humidity sensor mounted inside the cabinet
- **Outside sensor**: DHT22 sensor positioned in the ambient environment
- **Fan control**: Relay module connected to cabinet ventilation fans
- **Controller**: Raspberry Pi running the application

### Benefits
- **Energy efficient**: Fans only run when cooling is actually beneficial
- **Equipment protection**: Prevents overheating damage
- **Automated operation**: No manual intervention required
- **Cost effective**: Reduces electricity consumption compared to always-on systems
- **Scalable**: Can be applied to multiple cabinets or zones

This use case demonstrates how the application can bridge sensor data input with physical world control outputs to create practical automation solutions.

# Installation
* Download release file into the target RaspberryPI
* Unzip the file into a temp folder
* Export the following environment variable (see next section for installation and configuration options):
  * RPIC_DB_URL (default to "postgres://postgres:postgres@localhost:5432/rpic")
  * RPIC_REDIS_URL (default to "redis://localhost:6379/0")
  * RPIC_INFLUXDB (default to "BACKEND=rpi_controller.monitoring.backends.influxdb.InfluxDBv1SystemMonitor;LOCATION=influxdb://root:root@localhost:8086/rpic")
* The following environment variable are also available to customize the installation process:
  * RPIC_OPT (default to "/opt/rpic")
  * RPIC_WORKSPACE (default to "/var/rpic")
  * RPIC_DEBUG (default to "False")
  * RPIC_TIME_ZONE (default to "UTC)
  * RPIC_LOGGING_LEVEL (default to "ERROR")
  * RPIC_ENV (default to "PROD")
  * RPIC_SENTRY_DSN
* Run `sudo ./install` inside the temp folder
* During the first installation, automatically generated passwords (Django Admin, etc...) will be prompted
  * If you miss it, we can find it in ${RPIC_OPT}/app/.env
  * If you don't like it, you can change from the Django Admin UI

## External dependencies
The application requires the following external dependencies installed and configured:
* [Database](https://docs.djangoproject.com/en/5.2/ref/databases/)
  * Suggested: [PostgreSQL](https://www.postgresql.org/)
    * Installation options:
      * https://www.postgresql.org/download/
      * https://hub.docker.com/_/postgres
    * Required configurations:
      * Database: https://www.postgresql.org/docs/current/tutorial*createdb.html
* [Celery broker](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html)
  * Suggested:[Redis](https://redis.io/)
    * Installation options:
      * https://redis.io/downloads/
      * https://hub.docker.com/_/redis
* Time series database
  * At the moment, the only Monitoring System backend available is for [InfluxDB v1](https://docs.influxdata.com/influxdb/v1/)
    * Installation options:
      * https://docs.influxdata.com/influxdb/v1/introduction/install/
      * https://hub.docker.com/_/influxdb

## Security Notes
Application service MUST be executed as root user in order to make GPIO work properly.

Configured services will run with a dedicated "rpic" group.
Add your users to that group in order to manage the application executable and workspace files.

## Compatibility
The application has been tested on the following configurations:

| Hardaware | OS | PostgreSQL | Redis | InfluxDB |
| ------- | ------- | ------- | ------- | ------- |
| RaspberryPi 1b | Raspberry Pi OS (Legacy) Lite latest version | 13.18 | 6.0.16 | 1.6.7 |
| RaspberryPi 5 | Raspberry Pi OS (64*bit) Lite latest version | 17.5 | 8.0.3 | 1.11 |


# Architecture
For any architectural decision, please refer to the ["Architecture Decision Log"](docs/architecture-decision-log) inside the docs folder.

# Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding new features, or improving documentation, your pull requests are highly appreciated.
For developers looking to extend the project with custom functionality, you can easily integrate your own extensions by registering them in the dedicated registries located within the interface packages.
This modular approach allows you to seamlessly add new sensor types, actuators, or controllers while maintaining compatibility with the core system.
Please feel free to fork the repository, make your changes, and submit a pull request – we're excited to see what you'll build!

# Roadmap
## Documentation
* Detailed documentation on how to use the application
* Detailed documentation on how to contribute
* Detailed documentation on how to extend the system

## Features
* Upgrade to Django 5.2 (LTS)
* Implement a caching system for API calls
  * Improving performance by reducing DB access
* Implement System Monitor data export in the Admin UI
* Implement UI with graphs support for System Monitor
* Implement support for LoRa based devices
* Implement support for [ProgressiveWebApp](https://github.com/silviolleite/django-pwa)

## Security
* Protect UI and API with authentication and an authorization mechanism

## Infrastructure
* Expose the application and the static content through Nginx
  * For a small environment uWSGI could be enough, for medium to large environment Nginx would be better

## Installer
* Move installer to a dedicated Python(click) script
  * Better parameter management
* Move installer to docker compose

## CI/CD
* Expose coverage on Codcov
* Extende Ruff configuration to include more code checks
  * Evaluate if bandit can be then removed

# Known issues
* Sporadically the application crash with the following error: "Timed out waiting for PulseIn message. Make sure libgpiod is installed."
  * libgpiod process remains stuck: ```libgpiod_pulsein64 --pulses 81 --queue 8540 -i gpiochip0 17```
