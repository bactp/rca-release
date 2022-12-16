# syntax=docker/dockerfile:1
FROM python:3.6.9
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
#RUN source /bin/activate
CMD [ "python3", "rca-script.py", "--host=0.0.0.0" ]
