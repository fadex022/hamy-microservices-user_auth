from datetime import datetime
from typing import Optional
from uuid import uuid4

import logfire
import uvicorn
from fastapi import Depends, FastAPI, Header, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import auth, profile
from configuration.config import AuthSettings, ServerSettings
from handler_exception import (
    CustomBadGatewayException,
    EmailAlreadyUsedException,
    EmptyInputException,
    InactiveUserException,
    InvalidCredentialsException,
    InvalidPasswordException,
    InvalidTokenException,
    PhoneAlreadyUsedException,
    SameUsernamePasswordException,
    UserAlreadyExistsException,
    UserNotFoundException,
    UserNotValidException,
)

app = FastAPI(openapi_url="/auth/openapi.json", docs_url="/docs")

app.include_router(profile.router)
app.include_router(auth.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logfire.configure(send_to_logfire="if-token-present")
logfire.info("Auth Microservice Started")

# Logfire metrics counter to count all the request received by the microservice
request_counter = logfire.metric_counter(
    "request", unit="1", description="Number of requests received by auth microservice"
)


@app.middleware("http")
async def logfire_middleware(request: Request, call_next):
    request_counter.add(1)
    with logfire.span("{method} {path}", path=request.url.path, method=request.method):
        logfire.info("Request to access " + request.url.path)
        try:
            response = await call_next(request)
            logfire.info("Successfully accessed {path}", path=request.url.path)
        except Exception as e:
            logfire.error("Request to {request} failed: {e}", request=request.url, ex=e)
            response = JSONResponse(content={"success": False}, status_code=500)
        return response


def build_config():
    return AuthSettings()


def fetch_config():
    return ServerSettings()


@app.get("/index", status_code=status.HTTP_200_OK)
def index_auth(
    config: AuthSettings = Depends(build_config),
    fconfig: ServerSettings = Depends(fetch_config),
):
    return {
        "project_name": config.application,
        "webmaster": config.webmaster,
        "created": config.created,
        "development_server": fconfig.development_server,
        "dev_port": fconfig.dev_port,
    }


@app.get("/headers/verify", status_code=status.HTTP_200_OK)
def verify_headers(
    host: Optional[str] = Header(None),
    accept: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None),
    accept_encoding: Optional[str] = Header(None),
):
    return {
        "host": host,
        "accept": accept,
        "user_agent": user_agent,
        "accept_language": accept_language,
        "accept_encoding": accept_encoding,
    }


# @app.exception_handler(GlobalStarletteHTTPException)
# def global_exception_handler(req: Request, ex: str):
#     return PlainTextResponse(f"Error message: {ex}", status_code=400)
#
#
# @app.exception_handler(RequestValidationError)
# def validation_error_exception_handler(req: Request, ex: str):
#     return PlainTextResponse(f"Error message: {ex}", status_code=400)


@app.exception_handler(InvalidCredentialsException)
@logfire.instrument("InvalidCredentialsException")
def invalid_credentials_exception_handler(
    req: Request, ex: InvalidCredentialsException
):
    """
    Exception handler for InvalidCredentialsException.

    :param req: The incoming request object.
    :param ex: The InvalidCredentialsException object raised.
    :return: A JSONResponse object with the appropriate status code and message.
    """
    return JSONResponse(
        status_code=ex.status_code,
        content={"message": f"{ex.detail}"},
        headers=ex.headers,
    )


@app.exception_handler(UserNotFoundException)
@logfire.instrument("UserNotFoundException")
def user_not_found_exception_handler(req: Request, ex: UserNotFoundException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(UserAlreadyExistsException)
@logfire.instrument("UserAlreadyExistsException")
def user_already_exists_exception_handler(req: Request, ex: UserAlreadyExistsException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(InvalidPasswordException)
@logfire.instrument("InvalidPasswordException")
def invalid_password_exception_handler(req: Request, ex: InvalidPasswordException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(UserNotValidException)
@logfire.instrument("UserNotValidException")
def user_not_valid_exception_handler(req: Request, ex: UserNotValidException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(EmptyInputException)
@logfire.instrument("EmptyInputException")
def empty_input_exception_handler(req: Request, ex: EmptyInputException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(InvalidTokenException)
@logfire.instrument("InvalidTokenException")
def invalid_token_exception_handler(req: Request, ex: InvalidTokenException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(CustomBadGatewayException)
@logfire.instrument("CustomEmptyInputException")
def custom_empty_input_exception_handler(req: Request, ex: CustomBadGatewayException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(SameUsernamePasswordException)
@logfire.instrument("SameUsernamePasswordException")
def same_username_password_exception_handler(
    req: Request, ex: SameUsernamePasswordException
):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(InactiveUserException)
@logfire.instrument("InactiveUserException")
def inactive_user_exception_handler(req: Request, ex: InactiveUserException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(EmailAlreadyUsedException)
@logfire.instrument("EmailAlreadyUsedException")
def email_already_used_exception_handler(req: Request, ex: EmailAlreadyUsedException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


@app.exception_handler(PhoneAlreadyUsedException)
@logfire.instrument("PhoneAlreadyUsedException")
def phone_already_used_exception_handler(req: Request, ex: PhoneAlreadyUsedException):
    return JSONResponse(status_code=ex.status_code, content={"message": f"{ex.detail}"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
