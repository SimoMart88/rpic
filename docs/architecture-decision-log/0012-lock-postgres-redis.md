# PostgreSQL to Redis lock migration

Date: 24/09/2025

# Problem
Lock an entire record using select_for_update prevent device update during control operation execution

# Decision
* Move lock to Redis to prevent parallel control operation execution
* Control operation execution perform DB update only for required fields

# Consequences
* Control operation now depends on Redis

# Considered alternatives
* See "ADL 0001 - SQLite to PostgreSQL DB migration" for more details
