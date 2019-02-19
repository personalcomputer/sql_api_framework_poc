## Introduction
GET /sqlapi/SELECT id,lat,lng,coord_pair FROM todos_locations
GET /sqlapi/SELECT lat,lng FROM todos_locations
GET /sqlapi/SELECT point FROM todos_locations
GET /sqlapi/SELECT id FROM todos_locations LIMIT 1
GET /sqlapi/SELECT id FROM todos_locations WHERE name='test2'
GET /sqlapi/SELECT id,summary FROM todos_todo_items
GET /sqlapi/SELECT id,summary,location.lat,location.lng FROM todos_todo_items

Note: For ease of reading, these example URLs do not have special characters URL-encoded.

## Install & Run Proof of Concept

An example series of commands to run the demo, using docker:
```bash
docker build . --tag sql_api_framework_poc
docker run -d -p 6432:5432 -e POSTGRES_USER=django -e POSTGRES_PASS=well_known -e POSTGRES_DBNAME=sqlapi kartoza/postgis:11.0-2.5
docker run sql_api_framework_poc python3 /app/manage.py migrate
docker run -d -p 8000:8000 sql_api_framework_poc
```
