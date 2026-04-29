import traceback
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

from generator import check_input, generate_slides
from renderer import render_slide_html

app = FastAPI(title="LinkedIn Karussell Generator")

BASE_DIR = Path(__file__).parent


def _log_usage(client: str, topic: str, slides_count: int):
    timestamp = datetime.now().isoformat(timespec="seconds")
    print(
        f'[USAGE] {timestamp} | client="{client}" | topic="{topic}" | slides={slides_count}',
        flush=True,
    )

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

        # Insight-Zaehler fuer die Nummerierung
        insight_counter = 0
        slides_html = []
        for i, slide in enumerate(slides):
            if slide["type"] == "insight":
                insight_counter += 1
                current_insight = insight_counter
            else:
                current_insight = 0

            html = render_slide_html(
                slide=slide,
                index=i,
                total=len(slides),
                insight_number=current_insight,
            )
            slides_html.append(html)

        _log_usage(client, topic, len(slides))
        return JSONResponse({"slides_html": slides_html})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
