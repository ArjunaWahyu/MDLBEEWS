# FROM python:3.8
# FROM tensorflow/tensorflow:2.10.0-gpu
# lightest image for python
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

# CMD ["python", "main.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004", "--http", "h11"]
# CMD ["uvicorn", "main:app", "--port", "8004"]