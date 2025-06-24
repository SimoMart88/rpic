# pigpio to RPI_Adafruit_Python_DHT migration
Date: 24/06/2025

# Problem
pigpio crashes systematically after 3/4 hours, and services need to be manually restarted to make the system work again.

# Decision
* Implement a custom version of Adafruit_Python_DHT (https://github.com/adafruit/Adafruit_Python_DHT)
  * Create a repository fork: https://github.com/SimoMart88/RPI_Adafruit_Python_DHT
  * Implement a library version that works ONLY for RaspberryPI (no more compatibility with Beaglebone Black)
  * Implement support for the installation with Uv.
* Include RPI_Adafruit_Python_DHT as a dependency of this project
* Update code to us RPI_Adafruit_Python_DHT instead of pigpio

# Consequences
* The System will depend on a deprecated library "resumed" by a repository fork

# Considered alternatives
* Adafruit_CircuitPython_DHT
  * See "ADL 0002 - Adafruit_CircuitPython_DHT to pigpio migration" for all the details
