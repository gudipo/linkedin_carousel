import json
import os
import traceback
from datetime import datetime
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
LOG_PATH = BASE_DIR / "output" / "usage_log.jsonl"


def _log_usage(client: str, topic: str, answers_count: int, pdf_path):
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "client": client,
        "topic": topic,
        "answers_count": answers_count,
        "pdf_bytes": Path(pdf_path).stat().st_size,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

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
    extra_answers = [a.strip() for a in extra.split("||") if a.strip()] if extra else []
    try:
        result = check_input(topic, bullets, extra_answers)
        return JSONResponse(result)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/generate")
async def generate(
    topic: str = Form(...),
    bullets: str = Form(...),
    extra: str = Form(""),
    client: str = Form(""),
):
    extra_answers = [a.strip() for a in extra.split("||") if a.strip()] if extra else []
    try:
        slides_json = generate_slides(topic, bullets, extra_answers)
        slides = slides_json["slides"]
        pdf_path = await render_to_pdf(slides)
        _log_usage(client, topic, len(extra_answers), pdf_path)
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename="linkedin_karussell.pdf",
            background=None,
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
