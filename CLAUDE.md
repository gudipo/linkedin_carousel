# LinkedIn Karussell Generator

Web-App die LinkedIn-Karussell-Posts als PDF generiert. Kunden geben Thema und Stichpunkte ein, Claude erstellt die Slide-Inhalte, der Browser rendert das PDF.

## Architektur

- **Backend (FastAPI):** Nimmt Input entgegen, ruft Claude API auf, rendert Slide-HTML via Jinja2, gibt HTML-Strings als JSON zurueck
- **Frontend:** Rendert die HTML-Slides in iframes, erstellt das PDF client-seitig mit html2canvas + jsPDF
- **Hosting:** Render.com Free Tier (Docker)

## Dateien

```
main.py             # FastAPI App mit /check und /generate Endpoints
generator.py        # Claude API Aufrufe (check_input, generate_slides)
renderer.py         # Jinja2 HTML-Rendering der Slides
templates/
  index.html        # Web-UI mit Client-Side PDF-Erzeugung
  slide.html        # Slide-Template (1080x1080px, alle Slide-Typen)
static/
  main.css          # Dark-Theme UI Stylesheet
  neam_logo.svg     # Markenlogo
  fonts/            # IBM Plex Sans (woff2, self-hosted)
Dockerfile          # python:3.12-slim basiert
render.yaml         # Render.com Blueprint
.env                # ANTHROPIC_API_KEY (nicht committen!)
```

## Slide-Typen

hook, problem, insight (nummeriert), takeaway, cta - jeweils mit eigenem Layout und Farbschema im slide.html Template.

## Entwicklung

```bash
pip install -r requirements.txt
uvicorn main:app --port 8080
```

## Deployment

Push zu GitHub deployed automatisch auf Render.com. ANTHROPIC_API_KEY als Environment Variable in Render gesetzt.

## Kosten

- Hosting: 0 EUR (Render Free Tier, App schlaeft nach 15 Min Inaktivitaet)
- Claude API: ~0.01-0.03 EUR pro Karussell-Generierung (Sonnet)
- Sprache im Karussell: Deutsch, formelle Anrede (Sie)
