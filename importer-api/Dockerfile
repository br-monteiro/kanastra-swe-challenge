FROM python:3.12.2-alpine3.18

ENV PYTHONPATH=/opt/app
WORKDIR /opt/app

COPY requirements.txt .
COPY ./src /opt/app/src


RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]