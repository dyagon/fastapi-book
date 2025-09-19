class AuthException(Exception):
    #: short-string error code
    error = None
    #: long-string to describe this error
    description = ""
    #: web page that describes this error
    uri = None

    def __init__(self, error=None, description=None, uri=None):
        if error is not None:
            self.error = error
        if description is not None:
            self.description = description
        if uri is not None:
            self.uri = uri

        message = f"{self.error}: {self.description}"
        super().__init__(message)

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.error}">'



class OAuthError(AuthException):
    error = "oauth_error"


class MissingRequestTokenError(OAuthError):
    error = "missing_request_token"


class MissingTokenError(OAuthError):
    error = "missing_token"


class TokenExpiredError(OAuthError):
    error = "token_expired"


class InvalidTokenError(OAuthError):
    error = "token_invalid"


class UnsupportedTokenTypeError(OAuthError):
    error = "unsupported_token_type"


class MismatchingStateError(OAuthError):
    error = "mismatching_state"
    description = "CSRF Warning! State not equal in request and response."
