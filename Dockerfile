FROM python:3.8
COPY requirements.txt /var/requirements.txt
RUN pip install -r /var/requirements.txt