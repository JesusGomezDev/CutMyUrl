from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Base

DATABASE_URL = "sqlite:///urls.db"

engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

session = Session(engine)

session.close()