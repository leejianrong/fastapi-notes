from contextlib import contextmanager
from sqlmodel import Session
from app.db.session import engine

@contextmanager
def session_scope():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_session():
    with session_scope() as s:
        yield s