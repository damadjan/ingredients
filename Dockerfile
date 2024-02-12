FROM python:3.10

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

EXPOSE 8084

COPY . .

CMD ["python3", "main.py"]