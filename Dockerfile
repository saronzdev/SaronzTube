FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Crear directorio para descargas
RUN mkdir -p tmp

# Comando para ejecutar el bot
CMD ["python", "main.py"]
