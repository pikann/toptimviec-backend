FROM python:3.8

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["gunicorn", "--worker-class eventlet -w 1 run:app"]