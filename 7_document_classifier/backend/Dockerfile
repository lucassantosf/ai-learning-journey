FROM python:3.11-slim

WORKDIR /app

# instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar código
COPY . .

# rodar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]