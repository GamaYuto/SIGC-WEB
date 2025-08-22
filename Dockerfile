# Imagen base
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala librerías del sistema necesarias para ibm_db
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    unixodbc \
    unixodbc-dev \
    libxml2 \
    libxml2-dev \
    libffi-dev \
    curl \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
RUN pip install --no-cache-dir Flask ibm_db

# Copia la app
COPY app/ .
COPY static/ static/
COPY templates/ templates/

# Exponer puerto
EXPOSE 5000

# Ejecutar Flask
CMD ["python", "-m", "app.app"]
