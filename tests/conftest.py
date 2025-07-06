# tests/conftest.py
import pytest

from football_news.storage.db import Base, engine


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Create tables (and drop afterwards) for the entire test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)  # optional clean-up


@pytest.fixture(autouse=True)
def clean_db(create_test_tables):  # Add dependency on create_test_tables
    """Clean database before each test."""
    from football_news.storage.db import SessionLocal
    from football_news.storage.models import Story

    session = SessionLocal()
    try:
        session.query(Story).delete()
        session.commit()
    finally:
        session.close()
    yield
