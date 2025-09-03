
from pydantic import BaseModel

class SingleShortUrlCreateDTO(BaseModel):
    
    long_url: str
    short_url: str = "http://127.0.0.1:8000/s"

    visits_count: int = 0
    short_tag: str = ""
    created_by: str = ""

    msg_content: str = ""