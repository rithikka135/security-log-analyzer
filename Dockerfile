FROM python:3.11

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/backend

CMD ["python", "app.py"]