# Celery as the system to asynchronous and scheduled operations

Date: 08/05/2025

# Problem
System needs to perform asynchronous (long running tasks) and schedule (periodic task) operations

# Decision
* Use Celery (https://docs.celeryq.dev/en/stable/index.html)
* Use django-celery-beat (https://django-celery-beat.readthedocs.io/en/latest/) to allow periodic task configuration at run time

# Consequences
* Celery broker needs to be installed and configured
* Celery service(s) needs to be installed in host system

# Considered alternatives
* Dramatiq (https://dramatiq.io/)
  * Needs extra dependency to work with Django (https://dramatiq.io/cookbook.html#django)
  * Needs extra dependency to support scheduled tasks (https://dramatiq.io/cookbook.html#scheduling-messages)
