from football_news.storage.db import engine, Base

Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
