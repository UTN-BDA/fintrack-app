from flask import Flask
from flask_migrate import Migrate
from app.config.config import config
from app.config.cache_config import cache_config
from app.resources.routes import RouteApp
from flask_caching import Cache
import os
from app.extensions import db

migrate = Migrate()
cache = Cache()

def create_app():
    app_context = os.getenv("FLASK_CONTEXT")
    print(f"app_context: {app_context}")

    app = Flask(
        __name__,
        template_folder="fronted/templates",  # Ruta a la carpeta templates
        static_folder="fronted/static"       # Ruta a la carpeta static
    )

    configuration = config[app_context if app_context else 'development']
    app.config.from_object(configuration)
    app.secret_key = os.getenv('SECRET_KEY')
    
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app, config=cache_config)
    
    route = RouteApp()
    route.init_app(app)

    return app