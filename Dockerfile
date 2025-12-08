FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/manage.py

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
