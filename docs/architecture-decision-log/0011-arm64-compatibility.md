# Compatibility with ARM64 architecture
Date: 12/07/2025

# Problem
RPI_Adafruit_Python_DHT works fine for old RaspberryPI version but it's based on a deprecated library
and it's not compatible with the new RP1 chip used by RaspberryPI 5

# Decision
Implement a compatibility layer to make the system work with different hardware interface libraries

# Consequences
Increase the system complexity but increase hardware compatibility

# Considered alternatives
* Create different versions of the system using branches to make the user able to use different hardware interface libraries
  * High maintenance on the long term
