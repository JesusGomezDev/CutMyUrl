import os
from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate, limiter
from .routes import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    origin_allowed = os.getenv('ORIGIN_ALLOWED', 'http://localhost:4321')
    CORS(
        app,
        origins=[origin_allowed],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"]
    )

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    app.register_blueprint(api_bp, url_prefix='')

    return app