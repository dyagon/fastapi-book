

from fastapi import FastAPI

from .app.routers.hospital import router_hospital
from .app.routers.doctor import router_doctor

from fastapi_book.utils import register_custom_docs

app = FastAPI(
    title="Hospital",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
)

register_custom_docs(app)

app.include_router(router_hospital)
app.include_router(router_doctor)
