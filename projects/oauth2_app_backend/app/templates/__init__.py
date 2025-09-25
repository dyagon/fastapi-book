

from pathlib import Path

from fastapi.templating import Jinja2Templates


# Initialize templates
template_dir = Path(__file__).parent
templates = Jinja2Templates(directory=template_dir)
