"""
Gemini-pro one-sentence summariser.
Falls back to naïve truncation when GEMINI_API_KEY is absent.
"""

from __future__ import annotations
import os
import asyncio
import textwrap

try:
    import google.generativeai as genai
except ImportError:  # running tests w/out the lib
    genai = None  # type: ignore

API_KEY = os.getenv("GEMINI_API_KEY")
gen_client = None
if API_KEY and genai:
    genai.configure(api_key=API_KEY)
    gen_client = genai.GenerativeModel("gemini-pro")


async def summarise(title: str, body_html: str) -> str:
    """
    Returns ≤ 35-word single sentence.
    Gemini call is wrapped in asyncio.to_thread because SDK is sync.
    """
    if not gen_client:  # offline / no key
        plain = body_html.replace("<", " ").replace(">", " ")
        return textwrap.shorten(plain, 140)

    prompt = (
        "You are a football news sub-editor.\n"
        "Summarise the following article in ONE concise sentence (≤ 35 words).\n\n"
        f"Title: {title}\n\n"
        f"HTML body (trimmed):\n{body_html[:4000]}"
    )

    def _call():
        resp = gen_client.generate_content(
            prompt,
            safety_settings={
                "HARASSMENT": "BLOCK_NONE",
                "HATE": "BLOCK_NONE",
                "SEXUAL": "BLOCK_NONE",
                "DANGEROUS": "BLOCK_NONE",
            },
        )
        return resp.text.strip()

    return await asyncio.to_thread(_call)
