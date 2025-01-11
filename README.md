## Introduction

I have noticed a proliferation of new specialized query languages + web based protocols gaining traction in the last few years, especially GraphQL. However, when reviewing them and what developers praise about them, I became suspicious that they are largely redundant re-engineering that could have been solved by using the venerable and boring SQL.

In order to better understand the usecases and to check my suspicion, I made this experimental POC for what a SQL-based API framework for backend service development based on an HTTP transport layer would look like.

Note that this is NOT a direct database interface.  There is no SQL-passthrough to the RDBMS. All the normal web app API machinery is present, the full layer of abstraction enabling you to manage data consistency and trigger actions unrelated to your database, etc. Just e.g. this API design decides to write data when it sees the sql keyword "INSERT" as opposed to how a traditional REST api might use the HTTP verb "POST" for that purpose, etc. You have to explicitly define every single API resource that is accessible, and explicitly implement their underlying database queries (if they even get data from a DB at all)(in this example POC, Django ORM is used, so actually SQL is not even used at all by the API implementation code for talking to the RDBMS).

The advantage over something like REST is that rest is wildly inconsistent about e.g. how do you specify a max number of results to get back. Is it `?max=50`, `?max_results=50`, `?page_size=50`, etc. Every API does it differently. SQL is an actual consistent deep standard that thought about these usecases. In SQL, the answer is always the same, you always write `LIMIT 50`. Shouldn't web developers be able to have such powerful consistency available to them too instead of spending their lives reading and writing inconsistent API docs? GraphQL solved this. But so did SQL, and SQL did it better and is much more widely known, so I wanted to explore a world of SQL-based APIs.

## Examples
#### Query a List of TODOs
`GET /sqlapi/SELECT id, summary FROM todos_todo_items LIMIT 2`
```json
{
  "results": [
    {
      "id": "49f880a9-6d5b-4189-9f2f-90787a197117",
      "summary": "Move fast"
    },
    {
      "id": "a44a2731-f7b8-4ada-928d-e4569ef3b94d",
      "summary": "Break things"
    }
  ]
}
```

#### Query a List of TODOs, with Nested Location Data (Implicit JOIN)
`GET /sqlapi/SELECT id, summary, location.lat, location.lng FROM todos_todo_items LIMIT 2`
```json
{
  "results": [
    {
      "id": "49f880a9-6d5b-4189-9f2f-90787a197117",
      "summary": "Move fast",
      "location": {
        "lat": 37.481212,
        "lng": -122.152517
      }
    },
    {
      "id": "a44a2731-f7b8-4ada-928d-e4569ef3b94d",
      "summary": "Break things",
      "location": {
        "lat": 37.481212,
        "lng": -122.152517
      }
    }
  ]
}

```

#### Query a List of Locations
`GET /sqlapi/SELECT lat, lng FROM todos_locations LIMIT 3`
```json
{
  "results": [
    {
      "id": "132cadb6-d64d-45e5-a743-d91035a94bb8",
      "name": "test2",
      "lat": 37.778877,
      "lng": -122.396293
    }
  ]
}
```

#### Query a Specific Location
`GET /sqlapi/SELECT id, name, lat, lng FROM todos_locations WHERE name='test2'`
```json
{
  "results": [
    {
      "lat": 37.782305,
      "lng": -122.397391
    },
    {
      "lat": 37.778877,
      "lng": -122.396293
    },
    {
      "lat": 37.783757,
      "lng": -122.394922
    }
  ]
}

```

Note: For ease of reading, these example URLs do not have special characters URL-encoded.

## Install & Run Proof of Concept

An example series of commands to run the demo, using docker:
```bash
docker build . --tag sql_api_framework_poc
docker run -d -p 6432:5432 -e POSTGRES_USER=django -e POSTGRES_PASS=well_known -e POSTGRES_DBNAME=sqlapi kartoza/postgis:11.0-2.5
docker run sql_api_framework_poc python3 /app/manage.py migrate
docker run -d -p 8000:8000 sql_api_framework_poc
```
