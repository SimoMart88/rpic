# Use django-compressor to minimize JavaScript and CSS

Date: 05/02/2025

# Problem
Big Javascript and CSS files requires more time and resources usage by the clients in order to be loaded

# Decision
* Minimize Javascript and CSS files
* Use https://github.com/django-compressor/django-compressor

# Consequences
* Javascript and CSS files are loaded faster by the clients
* Due to how django-compressor works, when Javascript and CSS are update the clients cache is automatically refreshed
  * See the documentation here: https://django-compressor.readthedocs.io/en/stable/usage.html

# Considered alternatives
* https://github.com/jazzband/django-pipeline
  * More complex solution due configuration and manual installation of JavaScript modules required
