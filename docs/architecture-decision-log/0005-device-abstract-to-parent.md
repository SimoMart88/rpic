# Move Device model from abstract to a parent common class
Date: 06/02/2025

# Problem
Device as an abstract model means that every concrete class derive from it will create a new table with same columns.

Most of the query are be performed on Device "common" columns, having multiple tables makes DB maintenance more complex.

# Decision
Move from "Abstract base classes" to "Multi-table inheritance" for the Device children models

# Consequences
* Less DB tables to manage

# Considered alternatives
