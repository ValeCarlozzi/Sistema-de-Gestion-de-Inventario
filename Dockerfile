# Usamos una imagen oficial de Python ligera
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0 para que escuche conexiones externas al contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]