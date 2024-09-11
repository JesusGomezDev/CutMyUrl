from flask import Flask
from .extensions import db, migrate
from .routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar blueprints
    app.register_blueprint(api_bp, url_prefix='')

    return app
