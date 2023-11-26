FROM python:3.10-slim

WORKDIR /app/api
COPY . /app/api

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 5000

ENV NAME api

# Run app.py when the container launches
CMD ["python", "api.py"]