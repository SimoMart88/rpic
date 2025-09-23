# Force clean-up for PulseIO processes

Date: 24/09/2025

# Problem
Device control operations sometime fails with the following error:
"Timed out waiting for PulseIn message. Make sure libgpiod is installed."

Library adafruit_dht use PulseIo to control the GPIO \
See https://github.com/adafruit/Adafruit_CircuitPython_DHT/blob/main/adafruit_dht.py#L83

PulseIO spawn a new process to perform the operations and try to clean it up at the end of the execution using atexit library.\
See https://github.com/adafruit/Adafruit_Blinka/blob/main/src/adafruit_blinka/microcontroller/bcm283x/pulseio/PulseIn.py#L31

When called from uWSGI or Celery, atexit is not triggered and the process is left open preventing worker to complete.

# Decision
* Forcefully perform clean up operation by replicating the PulseIn.final function logic directly from the system.
  * Logic has to be improved with a proper error management

# Consequences
* System must be aware of PulseIO internal logic

# Considered alternatives
* Implement a control thread to kill all the worker child processes after a configurable timeout
  * Sensibly increase the system complexity
