# SQLite to PostgreSQL DB migration

Date: 12/01/2025

# Problem
DHT22 sensor can only be queried for results every 5 seconds.
System has to protect sensor from concurrent usage.

# Decision
* Use select_for_update option to control same sensor usage from multiple sources.
    * SQLite does not support select_for_update: https://docs.djangoproject.com/en/4.2/ref/models/querysets/#select-for-update
* Move from SQLite3 to PostgreSQL DB

# Consequences
* DHT22 sensor queries are now sequential

# Considered alternatives
* Shared lock solution like RedisLock
  * Usage of an extra DB like Redis increase the complexity and require more resources on the target hardware
