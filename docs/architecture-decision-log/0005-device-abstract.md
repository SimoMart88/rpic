# Move Device model as abstract
Date: 06/02/2025

# Problem
Device as an abstract model means that every concrete class derive from it will create a new table with same columns.

Most of the queries requires "children" classes specific field like the 'interface' column.

Create a "parent" table with common columns requires extra joins when data are retrieved.

# Decision
Use Django "Abstract base classes" solution for the Device children models

# Consequences
* More DB tables to maintain with duplicated columns

# Considered alternatives
* Django "Multi-table inheritance" solution
  * Requires extra DB joins to retrieve the data
