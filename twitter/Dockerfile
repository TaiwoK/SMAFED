FROM python:3.7-alpine

EXPOSE 9009

WORKDIR /app

COPY ./twitter_app.py /app
COPY ./requirements.txt /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./twitter_app.py"]