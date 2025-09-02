
from fastapi import FastAPI

app = FastAPI(
    title="Chapter 9 - Security Examples",
    version="0.1.0")

from .auth.http_basic import app as http_basic_app
from .auth.http_digest import app as http_digest_app
from .auth.api_key import app as api_key_app
# from .oauth2.m2m import app as oauth2_m2m_app
# from .oauth2.main_old import app as oauth2_auth_app

app.mount("/http-basic", http_basic_app, name="http_basic")
app.mount("/http-digest", http_digest_app, name="http_digest")
app.mount("/api-key", api_key_app, name="api_key")
# app.mount("/m2m", oauth2_m2m_app, name="oauth2_m2m")
# app.mount("/auth", oauth2_auth_app, name="oauth2_auth")
