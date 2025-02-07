# Implement a UI to update data asynchronously
Date: 19/01/2025

# Problem
UI loads slowly on legacy device like RaspberryPi 1b+ (hardware I'm now using)

# Decision
* Store device status data on the DB to be loaded faster from the UI.
* Call an API to asynchronously "use" the device and update the data on the UI.
  * UI is also "beautified" by asynchronously call.

# Consequences
* Homepage loads with data available on the DB and refresh it only later
* If client does not support JavaScript, device status is not updated
