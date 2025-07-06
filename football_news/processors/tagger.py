"""
Phrase-matcher tags (clubs, leagues, players) → Story.tags list.
Extend phrases in config/vocab.yml – no code changes needed.
"""

from __future__ import annotations
from pathlib import Path
import yaml
import re

import spacy
from spacy.matcher import PhraseMatcher

_nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "lemmatizer"])
_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")

# -- load phrases -------------------------------------------------------------
_vocab = yaml.safe_load(Path("config/vocab.yml").read_text())
for label, phrases in _vocab.items():
    _matcher.add(label, [_nlp.make_doc(p) for p in phrases])

# -----------------------------------------------------------------------------


def tag(text: str) -> list[str]:
    doc = _nlp(text)
    found = {_nlp.vocab.strings[mid] for mid, _, _ in _matcher(doc)}

    # heuristic extras
    if re.search(r"\bworld cup\b", text, re.I):
        found.add("world_cup")

    return sorted(found)
