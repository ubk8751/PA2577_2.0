FROM python:3.10

WORKDIR /app
COPY . .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN pip install --upgrade setuptools
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 5001

ENV NAME user_management

CMD ["python", "./src/user_management/user.py"]