from flask import Flask, Blueprint, jsonify, redirect, request
from flask_restful import Api, Resource
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from app.models import Urls
import random
import string
from datetime import datetime

DATABASE_URL = "sqlite:///urls.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(SessionLocal)

app = Flask(__name__)

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Configurar CORS con origen permitido
CORS(api_bp, origins=["http://localhost:4321"])

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class Shorten(Resource):
    def post(self):
        db_session = session()
        try:
            data = request.get_json()
            if not data or 'original_url' not in data:
                return {'error': 'Invalid input'}, 400

            original_url = data['original_url']
            user_id = data['user_id']
            short_code = generate_short_code()

            while db_session.query(Urls).filter_by(short_code=short_code).first():
                short_code = generate_short_code()

            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_url = Urls(short_code=short_code, original_code=original_url, created_at=created_at, user_id=user_id)
            db_session.add(new_url)
            db_session.commit()

            return {'short_code': short_code}
        except Exception as e:
            db_session.rollback()
            print(f"Error during POST /shorten: {e}")
            return {'error': 'Internal server error'}, 500
        finally:
            db_session.close()

class Redirect(Resource):
    def get(self, short_code):
        print(f"Received short_code: {short_code}")
        db_session = session()
        try:
            url = db_session.query(Urls).filter_by(short_code=short_code).first()
            if url:
                print(f"Redirecting to: {url.original_code}")
                return redirect(url.original_code)
            else:
                print("URL not found")
                return {'error': 'URL not found'}, 404
        except Exception as e:
            print(f"Error during GET /{short_code}: {e}")
            return {'error': 'Internal server error'}, 500
        finally:
            db_session.close()

class Recents(Resource):
    def get(self, user_id):
        print(f"Received user_id: {user_id}")
        db_session = session()
        try:
            urls = db_session.query(Urls).filter_by(user_id=user_id).order_by(Urls.created_at.desc()).limit(5).all()
            if urls:
                response = [
                    {
                        "shortUrl": f"https://cutmyurl.link/{url.short_code}",
                        "originalUrl": url.original_code,
                        "date": url.created_at
                    }
                    for url in urls
                ]
                return jsonify(response)
            else:
                print("URLs not found")
                return {'error': 'URLs not found'}, 404
        except Exception as e:
            print(f"Error during GET /{user_id}: {e}")
            return {'error': 'Internal server error'}, 500
        finally:
            db_session.close()

api.add_resource(Shorten, '/shorten')
api.add_resource(Redirect, '/<short_code>')
api.add_resource(Recents, '/links/<user_id>')

app.register_blueprint(api_bp, url_prefix='')

if __name__ == '__main__':
    app.run(debug=True)