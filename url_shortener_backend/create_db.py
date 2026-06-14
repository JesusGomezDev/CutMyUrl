from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
from app.models import Base

DATABASE_URL = "sqlite:///urls.db"

engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

inspector = inspect(engine)
existing_columns = {col['name'] for col in inspector.get_columns('urls')}
if 'clicks' not in existing_columns:
    with engine.begin() as conn:
        conn.execute(text('ALTER TABLE urls ADD COLUMN clicks INTEGER NOT NULL DEFAULT 0'))

session = Session(engine)

session.close()