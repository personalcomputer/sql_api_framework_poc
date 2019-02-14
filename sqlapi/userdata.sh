python3 -m pip install -r requirements.txt

docker run -d -p 6432:5432 -e POSTGRES_USER=django -e POSTGRES_PASS=well_known -e POSTGRES_DBNAME=sqlapi kartoza/postgis:11.0-2.5
