from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"

jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


def render_slide_html(slide: dict, index: int, total: int, insight_number: int) -> str:
    template = jinja_env.get_template("slide.html")
    return template.render(
        slide=slide,
        index=index,
        total=total,
        insight_number=insight_number,
    )
