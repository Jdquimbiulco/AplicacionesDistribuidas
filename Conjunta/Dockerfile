FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependencias si existieran
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Publicar el puerto del servidor de chat (TCP 5000)
EXPOSE 5000

# Por defecto ejecuta el servidor de chat
CMD ["python", "servidor.py"]
