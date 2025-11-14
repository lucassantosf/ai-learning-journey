FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos o código apenas para permitir build inicial (mas ele será sobrescrito pelo volume)
COPY . .

EXPOSE 8000

# Use reload só em dev; o compose controlará isso
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]