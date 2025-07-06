from football_news.processors.summary import summarise
from football_news.processors.tagger import tag
import pytest


# --- Summary fallback works offline ------------------------------------------
@pytest.mark.asyncio
async def test_summary_fallback():
    text = "<p>Liverpool hammer Chelsea 4-0 at Anfield.</p>"
    s = await summarise("Liverpool 4-0 Chelsea", text)
    assert isinstance(s, str) and len(s) > 10


# --- Tagger matches ----------------------------------------------------------
def test_tagger():
    t = tag("Arsenal face Chelsea in London derby")
    assert "arsenal" in t and "chelsea" in t
