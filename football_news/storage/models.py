import datetime as dt
from sqlalchemy import Column, String, Text, DateTime, JSON

from .db import Base


class Story(Base):
    __tablename__ = "stories"
    id = Column(String, primary_key=True, index=True)  # GUID/URL hash
    title = Column(Text, nullable=False)
    link = Column(String, nullable=False)
    source = Column(String, index=True)
    published = Column(DateTime(timezone=True), default=dt.datetime.utcnow)
    raw = Column(Text)  # full RSS/HTML for debug
    summary = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
