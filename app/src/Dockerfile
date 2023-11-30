FROM python:3.10

WORKDIR /app

COPY . .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV NAME app

CMD ["python", "src/app.py"]
