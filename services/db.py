import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.db_models import Base

def get_database_url():
    url = os.environ.get('DATABASE_URL')
    if url:
        return url
    return 'sqlite:///eligify.db'

engine = create_engine(get_database_url(), future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

def init_db(app):
    Base.metadata.create_all(engine)
    @app.teardown_appcontext
    def _remove_session(_):
        SessionLocal.remove()