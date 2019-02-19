FROM ubuntu

RUN apt-get update
RUN apt-get install python3-pip python3 gdal-bin postgresql-client -y
RUN python3 -m pip install gunicorn

ADD ./requirements.txt /app/requirements.txt
RUN python3 -m pip install -r /app/requirements.txt

ADD . /app

CMD gunicorn /app/sql_api_framework_poc/wsgi.py --bind 0.0.0.0:8000
