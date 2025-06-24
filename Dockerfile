FROM python:3.12-slim-bookworm
ENV TZ=America/Argentina/Mendoza

ENV FLASK_CONTEXT=production
ENV PYTHONUNBUFFERED=1
ENV PATH=$PATH:/home/flaskapp/.local/bin

# Actualizamos los repositorios e instalamos las dependencias necesarias
RUN apt-get update && apt-get install -y \
    python3-dev \
    build-essential \
    libpq-dev \
    python3-psycopg2 \
    && ln -sf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY ./app ./app
COPY ./app.py .
COPY .env .env

# Añadir el archivo requirements.txt e instalar las dependencias de Python
ADD requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install gevent==24.10.3 gunicorn==23.0.0

# Exponer el puerto 5000 para Flask
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
#CMD ["gunicorn", "--workers", "2", "--threads", "8","--log-level", "INFO", "--bind", "0.0.0.0:5000", "app:create_app()"]
CMD ["flask", "run", "--host=0.0.0.0"]