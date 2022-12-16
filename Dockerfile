# syntax=docker/dockerfile:1
FROM python:3.8.10
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD [ "python3", "main.py", "--host=0.0.0.0" ]
