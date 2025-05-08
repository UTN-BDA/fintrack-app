from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config.config import config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app_context = os.getenv("FLASK_CONTEXT")
    print(f"app_context: {app_context}")

    app = Flask(__name__)
    configuration = config[app_context if app_context else 'development']
    app.config.from_object(configuration)
    
    db.init_app(app)
    migrate.init_app(app, db)

    return app