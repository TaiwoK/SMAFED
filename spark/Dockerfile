FROM  hontikyana/spark-mongo

COPY . /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./spark_app.py"]