import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def _parse_json(raw: str) -> dict:
    """Extrahiert JSON auch wenn Claude es in Markdown-Codeblöcke einwickelt."""
    raw = raw.strip()
    # Markdown-Codeblock entfernen
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return json.loads(raw)

CHECK_SYSTEM = """Du bist ein LinkedIn-Content-Experte. Deine Aufgabe: Prüfe ob der gegebene Input ausreicht,
um ein überzeugendes LinkedIn-Karussell mit 5-6 Slides zu erstellen.

Ein gutes Karussell braucht:
- Ein klares Thema mit einem starken Hook-Potenzial
- Mindestens 2 konkrete Insights oder Kernaussagen
- Eine Zielgruppe (explizit oder implizit erkennbar)
- Einen sinnvollen Call-to-Action

Antworte NUR mit validem JSON, kein Markdown, keine Erklärungen:
{
  "ready": true/false,
  "missing_info": ["Frage 1?", "Frage 2?"]
}

Wenn ready=true, ist missing_info ein leeres Array.
Stelle maximal 2 präzise, offene Fragen. Fragen auf Deutsch."""

GENERATE_SYSTEM = """Du bist ein LinkedIn-Content-Experte, der viral gehende Karussell-Posts erstellt.

Erstelle ein LinkedIn-Karussell mit genau 6 Slides nach dieser strikten Struktur:
1. HOOK: Scroll-Stopper. Provokante Frage, überraschende Zahl oder steile These. Sehr kurz, sehr fett.
2. PROBLEM: Warum ist das relevant? Empathischer Kontext, 2-3 Sätze.
3. INSIGHT 1: Erster Kernpunkt mit 2-3 konkreten Bullet Points.
4. INSIGHT 2: Zweiter Kernpunkt mit 2-3 konkreten Bullet Points.
5. TAKEAWAY: Das eine, das der Leser mitnehmen soll. Prägnant.
6. CTA: Klare Handlungsaufforderung. Kommentieren, folgen oder teilen.

Schreibe auf Deutsch. Sprache: direkt, klar, professionell aber nicht steif.
Bullet Points: kurz (max 8 Wörter), aktionsorientiert.
Hook: maximal 10 Wörter, endet idealerweise mit Fragezeichen oder Ausrufezeichen.

Antworte NUR mit validem JSON, kein Markdown:
{
  "slides": [
    {"type": "hook",    "headline": "...", "subtext": "..."},
    {"type": "problem", "title": "...",    "text": "..."},
    {"type": "insight", "title": "...",    "bullets": ["...", "...", "..."]},
    {"type": "insight", "title": "...",    "bullets": ["...", "...", "..."]},
    {"type": "takeaway","headline": "...", "text": "..."},
    {"type": "cta",     "headline": "...", "action": "..."}
  ]
}"""


def check_input(topic: str, bullets: str, extra_answers: list[str] = None) -> dict:
    """Prüft ob der Input für die Karussell-Generierung ausreicht."""
    content = f"Thema: {topic}\nStichpunkte: {bullets}"
    if extra_answers:
        content += "\nZusätzliche Infos:\n" + "\n".join(extra_answers)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=CHECK_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )

    raw = message.content[0].text.strip()
    return _parse_json(raw)


def generate_slides(topic: str, bullets: str, extra_answers: list[str] = None) -> dict:
    """Generiert die finalen Slide-Inhalte als JSON."""
    content = f"Thema: {topic}\nStichpunkte: {bullets}"
    if extra_answers:
        content += "\nZusätzliche Infos:\n" + "\n".join(extra_answers)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=GENERATE_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )

    raw = message.content[0].text.strip()
    return _parse_json(raw)
