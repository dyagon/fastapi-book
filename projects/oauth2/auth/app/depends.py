from fastapi import Depends, Form
from typing import Optional

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from typing import Optional, Literal

from ..domain.models import TokenRequest
from ..domain.models.auth import AuthorizeRequestForm
from ..domain.exception import UnauthorizedClientException

from ..domain.service import OAuth2Service, ClientRepo, UserRepo


def get_oauth2_service() -> OAuth2Service:
    return OAuth2Service(ClientRepo(), UserRepo())

