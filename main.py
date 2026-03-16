import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

from generator import check_input, generate_slides
from renderer import render_to_pdf

app = FastAPI(title="LinkedIn Karussell Generator")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/check")
async def check(
    topic: str = Form(...),
    bullets: str = Form(...),
    extra: str = Form(""),
):
    """
    Prüft ob der Input ausreicht. Gibt JSON zurück:
    { "ready": bool, "missing_info": ["Frage 1", ...] }
    """
    extra_answers = [a.strip() for a in extra.split("||") if a.strip()] if extra else []
    try:
        result = check_input(topic, bullets, extra_answers)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/generate")
async def generate(
    topic: str = Form(...),
    bullets: str = Form(...),
    extra: str = Form(""),
):
    """
    Generiert das Karussell-PDF und gibt es als Download zurück.
    """
    extra_answers = [a.strip() for a in extra.split("||") if a.strip()] if extra else []
    try:
        slides_json = generate_slides(topic, bullets, extra_answers)
        slides = slides_json["slides"]
        pdf_path = await render_to_pdf(slides)
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename="linkedin_karussell.pdf",
            background=None,
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
