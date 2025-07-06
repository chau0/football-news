from __future__ import annotations
from typing import Annotated

from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from football_news.storage.db import SessionLocal
from football_news.storage.models import Story

app = FastAPI(title="Football News API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# -- DB dependency ------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------------------------------------------


def _dto(obj: Story) -> dict:
    return {
        "id": obj.id,
        "title": obj.title,
        "link": obj.link,
        "source": obj.source,
        "published": obj.published.isoformat(),
        "summary": obj.summary,
        "tags": obj.tags,
    }


@app.get("/v1/news")
def list_news(
    limit: Annotated[int, Query(le=200)] = 50,
    tag: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    qry = db.query(Story).order_by(Story.published.desc()).limit(limit)
    if tag:
        qry = qry.filter(Story.tags.contains([tag]))
    if q:
        qry = qry.filter(Story.title.ilike(f"%{q}%"))
    return [_dto(r) for r in qry.all()]


@app.get("/v1/news/{story_id}")
def single_story(story_id: str, db: Session = Depends(get_db)):
    row = db.get(Story, story_id)
    if not row:
        raise HTTPException(404, detail="not found")
    return _dto(row)


@app.get("/v1/top")
def top_for_club(
    club: Annotated[str, Query(examples={"club": "arsenal"})],
    limit: Annotated[int, Query(le=100)] = 25,
    db: Session = Depends(get_db),
):
    qry = (
        db.query(Story)
        .filter(Story.tags.contains([club]))
        .order_by(Story.published.desc())
        .limit(limit)
    )
    return [_dto(r) for r in qry.all()]
