# Redis as Celery broker

Date: 08/05/2025

# Problem
Celery requires a broker system to store and retrieve messages

# Decision
* Use Redis (https://redis.io/)
  * Can be used as both a backend and a broker (https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html#redis)
  * Stable support (https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html#broker-overview)

# Consequences
* Can be used for Django cache (https://docs.djangoproject.com/en/4.2/topics/cache/#redis)
* can be use shared locks (https://github.com/jazzband/django-redis)

# Considered alternatives
* Django Message Broker (https://github.com/django-message-broker/django-message-broker)
  * This could avoid a dependency with an external system like Redis but, as per documentation, the solution has some limitations:
    * Prototyping, Testing, Training
    * Small systems with a low number of users.
