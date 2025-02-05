# Adafruit_CircuitPython_DHT to pigpio migration
Date: 12/01/2025

# Problem
CPU stack at 100% when DHT22 is queried for data

None of the solution mentioned here is working: https://github.com/adafruit/Adafruit_Blinka/issues/210

# Decision
* Move from Adafruit to pigpio
* No library is available PyPI for pigpio
  * An improved version of the code available here http://abyz.me.uk/rpi/pigpio/code/DHT.py has been used

# Consequences
* CPU is not stuck anymore and DHT22 is queried properly

# Considered alternatives
* Adafruit_DHT
  * Package is deprecated and cannot be directly installed via uv due to this issue: https://github.com/flyte/mqtt-io/issues/373
