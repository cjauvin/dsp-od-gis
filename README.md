# Dependencies

* Python 3.6+ (with pip)
* PostgreSQL 9.5+
* PostGIS 2.4+

# Scenario 1: Restore an already created database

```
$ pg_restore -C -d template1 central_routing_results_v3.dump
```

# Scenario 2: Create a new database from a JSON file

### Create an empty database

```
$ createdb central_routing_results_v3
$ psql -d central_routing_results_v3 -f schema.sql -v srid=3347
```

### Install Python dependencies

```
$ pip install -r requirements.txt
```

### Import the data

```
$ python json_to_sql.py central_routing_results_v3 3347 < central_routing_results_v3.json
```

# Example queries

```
central_routing_results_v3=# select count(*) from od;
 count
--------
 478599
(1 row)

central_routing_results_v3=# select count(*) from od_step;
  count
---------
 2493119
(1 row)

central_routing_results_v3=# select type, action from od join od_step using (od_id) where ipere = 1;
   type   | action
----------+---------
 access   | walking
          | board
          | unboard
 transfer | walking
          | board
          | unboard
 transfer | walking
          | board
          | unboard
 egress   | walking
(10 rows)

central_routing_results_v3=# select sum(st_length(geom)) from od join od_step using (od_id) where ipere = 1;
        sum
-------------------
 0.153636728953892
(1 row)
```
