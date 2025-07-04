from football_news.storage.db import engine, Base
from football_news.storage.models import Story  # noqa: F401

assert Story
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
