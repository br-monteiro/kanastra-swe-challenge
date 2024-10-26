FROM python:3.12.2-alpine3.18

ENV PYTHONPATH=/opt/app

WORKDIR /opt/app

COPY requirements.txt .
COPY ./src /opt/app/src

RUN pip install -r requirements.txt

EXPOSE ${METRICS_PORT}

CMD ["python", "src/main.py"]