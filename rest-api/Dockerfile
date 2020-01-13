FROM tiangolo/uwsgi-nginx-flask:python3.7

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt

COPY ./app /app

EXPOSE 80

