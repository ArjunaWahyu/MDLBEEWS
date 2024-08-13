FROM python:3.11-slim
# FROM tensorflow/tensorflow:2.10.0-gpu

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]