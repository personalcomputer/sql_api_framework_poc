docker run -d -p 8000:8000 ubuntu
RUN apt install python3-pip python3 gdal-bin postgresql-client vim iputils-ping -y
RUN python3 -m pip install -r requirements.txt
CMD ./manage.py runserver 0.0.0.0:8000

# docker run 'python3 /app/manage.py migrate'

docker run -d -p 6432:5432 -e POSTGRES_USER=django -e POSTGRES_PASS=well_known -e POSTGRES_DBNAME=sqlapi kartoza/postgis:11.0-2.5
