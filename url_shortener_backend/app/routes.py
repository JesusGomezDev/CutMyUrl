import os
from flask import Blueprint, jsonify, redirect, request, Response
from flask_restful import Api, Resource
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from dotenv import load_dotenv
from app.models import Urls
from app.extensions import limiter
import random
import string
import re
from urllib.parse import urlparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, '.env'))

SHORT_BASE_URL = os.getenv('SHORT_BASE_URL', 'https://shortenthis.link').rstrip('/')

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'urls.db')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = scoped_session(SessionLocal)

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

_SCHEME_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.\-]*://')

def validate_and_normalize_url(raw_url):
    if not isinstance(raw_url, str):
        return None

    url = raw_url.strip()
    if not url:
        return None

    if not _SCHEME_RE.match(url):
        url = 'https://' + url

    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return None
    if not parsed.netloc or '.' not in parsed.netloc:
        return None

    return url

class Shorten(Resource):
    decorators = [limiter.limit("10 per minute; 200 per day")]

    def post(self):
        db_session = session()
        try:
            data = request.get_json(silent=True)
            if not data or 'original_url' not in data:
                return {'error': 'Invalid input'}, 400

            original_url = validate_and_normalize_url(data.get('original_url'))
            if original_url is None:
                return {'error': 'Invalid URL. Only http and https URLs are allowed.'}, 400

            user_id = data.get('user_id')
            if not user_id or not isinstance(user_id, str):
                return {'error': 'Missing or invalid user_id'}, 400

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

NOT_FOUND_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Link not found</title>
    <style>
        body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
            background: #0b101b;
            color: #fff;
            text-align: center;
            padding: 1rem;
        }
        h1 {
            font-size: 4rem;
            margin: 0;
            background: linear-gradient(to right, #144EE3, #EB568E);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        p { color: #9aa4b2; font-size: 1.1rem; }
        a {
            margin-top: 1rem;
            color: #fff;
            text-decoration: none;
            background: #144EE3;
            padding: 0.6rem 1.4rem;
            border-radius: 9999px;
        }
        a:hover { background: #0f3bb0; }
    </style>
</head>
<body>
    <h1>404</h1>
    <p>This short link doesn't exist or has expired.</p>
    <a href="/">Shorten a new link</a>
</body>
</html>"""

class Redirect(Resource):
    def get(self, short_code):
        print(f"Received short_code: {short_code}")
        db_session = session()
        try:
            url = db_session.query(Urls).filter_by(short_code=short_code).first()
            if url:
                print(f"Redirecting to: {url.original_code}")
                url.clicks = (url.clicks or 0) + 1
                db_session.commit()
                return redirect(url.original_code)
            else:
                print("URL not found")
                return Response(NOT_FOUND_PAGE, status=404, mimetype='text/html')
        except Exception as e:
            db_session.rollback()
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
                        "shortUrl": f"{SHORT_BASE_URL}/{url.short_code}",
                        "originalUrl": url.original_code,
                        "date": url.created_at,
                        "clicks": url.clicks or 0
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