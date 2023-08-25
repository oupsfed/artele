FROM python:3.9-slim

RUN mkdir /app

COPY . /app

WORKDIR /app

RUN pip3 intall -r requirements.txt --no-cache-dir

CMD ["python", "main.py"]