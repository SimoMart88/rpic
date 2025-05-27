# Implement a custom and simplified UI for scheduled tasks

Date: 09/05/2025

# Problem
* Django Celery Beat comes with a high level of configurability but can result in complex for simple operation.
  * This is an example list of what information should to know to schedule a task for this application:
    * Task name (can eventually, by mistake, select a Sensor task to schedule an Actuator)
    * Task slug
    * Schedule type difference:
      * Clocked
      * Crontab
      * Interval
      * Solar events

# Decision
* Implement a custom panel in the Admin UI to allow user a Crontab only schedule with automatic parameter configuration

# Consequences
* Limited schedule type support

# Considered alternatives
* Leave active the already available Django Celery Beat UI and prepare detailed documentation for schedule configuration
