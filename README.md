
# 📊 Fintrack

Fintrack es una API REST para gestionar gastos personales o empresariales, desarrollada en Python con Flask y SQLAlchemy. La base de datos es PostgreSQL (dockerizado) y las migraciones se manejan con Alembic (Flask-Migrate).

---

## 🚀 Requisitos previos

- **Python** 3.11+  
- **Docker**  
- **PgAdmin**

---

## ⚙️ Instalación

1. **Clonar el repositorio**  
   ```bash
   git clone https://github.com/tu_usuario/fintrack.git
   cd fintrack

2. **Crear y activar un entorno virtual**  
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt

4. **Configuración de las variables de entorno**
Configuraremos el **.env** para poder conectarnos al servidor de base de datos.
   ```
   FLASK_APP = app.py
   FLASK_CONTEXT = development
   DEV_DB_URI = 'postgresql://usuario:contraseña@localhost:5440/fintrack'
   TEST_DB_URI = 'postgresql://usuario:contraseña@localhost:5440/fintrack_test'
   PROD_DB_URI = 'postgresql://usuario:contraseña@localhost:5440/fintrack_prod'
   ```
   
   
5. **Instalacion de servidor de base de datos**
Una vez ya creado el entorno virtual, configuraremos nuestro **.env**, en el repositorio dejamos un **.env-example** con la estructura que debemos seguir. Una vez ya configurado el **.env** nos moveremos a la carpeta dockers y a la subcarpeta fintrack_db.
   ```bash
   cd dockers
   cd fintrack_db
   ```
   
   Antes de levantar el contenedor, asegúrate de crear la red externa `fintrack_network`:
   ```bash
   docker network create fintrack_network
   ```

   Luego, ejecuta el siguiente comando para levantar el contenedor:
   ```bash
   docker compose up
   ```
   
- Una vez realizado esto ya tendriamos nuestro servidor de base de datos ya corriendo.


# Uso de Flask-Migrate
Flask-Migrate es una extensión que nos permite manejar migraciones de bases de datos SQLAlchemy para aplicaciones desarrolladas en Flask.

## Instalación
Para generar los cambios descritos en el script de migración, hay que ejecutar:

   `$ flask db upgrade`

Referencia:

- https://flask-migrate.readthedocs.io/en/latest/

# Levantar el proyecto
Una vez ya realizado todos los pasos anteriores podremos levantar el proyecto. 

   `$ flask run`

El proyecto ya estaria corriendo de manera local.
