# tests/conftest.py
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from football_news.storage.db import Base


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary database for testing."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    # Create engine for the temporary database
    engine = create_engine(f"sqlite:///{db_path}")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Patch the original engine and session
    from football_news.storage import db

    original_engine = db.engine
    original_session = db.SessionLocal

    db.engine = engine
    db.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield engine

    # Cleanup
    db.engine = original_engine
    db.SessionLocal = original_session
    os.close(db_fd)
    os.unlink(db_path)
