import asyncio
import uuid
import os
import img2pdf
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

TEMPLATES_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "output"

jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def _render_slide_html(slide: dict, index: int, total: int, insight_number: int) -> str:
    template = jinja_env.get_template("slide.html")
    return template.render(
        slide=slide,
        index=index,
        total=total,
        insight_number=insight_number,
    )


async def _screenshot_slide(page, html: str, png_path: str):
    await page.set_viewport_size({"width": 1080, "height": 1080})
    await page.set_content(html, wait_until="networkidle")
    await page.screenshot(path=png_path, clip={"x": 0, "y": 0, "width": 1080, "height": 1080})


async def render_to_pdf(slides_data: list[dict]) -> str:
    """
    Rendert eine Liste von Slide-Dicts zu einem PDF.
    Gibt den Pfad zur generierten PDF-Datei zurück.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    job_id = str(uuid.uuid4())[:8]
    png_paths = []

    # Insight-Zähler für die Nummerierung
    insight_counter = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for i, slide in enumerate(slides_data):
            if slide["type"] == "insight":
                insight_counter += 1
                current_insight = insight_counter
            else:
                current_insight = 0

            html = _render_slide_html(
                slide=slide,
                index=i,
                total=len(slides_data),
                insight_number=current_insight,
            )

            png_path = str(OUTPUT_DIR / f"{job_id}_slide_{i:02d}.png")
            await _screenshot_slide(page, html, png_path)
            png_paths.append(png_path)

        await browser.close()

    pdf_path = str(OUTPUT_DIR / f"{job_id}_carousel.pdf")
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(png_paths))

    # Temporäre PNGs löschen
    for png in png_paths:
        try:
            os.remove(png)
        except OSError:
            pass

    return pdf_path


def render_pdf_sync(slides_data: list[dict]) -> str:
    """Synchroner Wrapper für FastAPI-Background oder direkten Aufruf."""
    return asyncio.run(render_to_pdf(slides_data))
