from datetime import datetime, timedelta
from typing import Annotated

import jwt
import logfire
from fastapi import Depends, Security
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import ValidationError

from handler_exception import InvalidCredentialsException, InactiveUserException
from models.data.users import Login
from models.request.token import TokenData
from service.auth import AuthService

SECRET_KEY = "a8c15b3988f0b523a24813041c7ac27a19c2ba4efdf548a3e4ce0d75873a1ee2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

crypt_context = CryptContext(schemes=["sha256_crypt", "md5_crypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes={
        "admin:read": "admin role that has read only role",
        "admin:write": "admin role that has write only role",
        "user:read": "user role that has read only role",
        "user:write": "user role that has write only role",
    }
)


def create_access_token(data: dict, expires_after: timedelta | None = None):
    to_encode = data.copy()
    if expires_after:
        expire = datetime.now() + expires_after
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password):
    return crypt_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return crypt_context.verify(plain_password, hashed_password)


def authenticate(password, account: Login):
    return verify_password(password, account.password)


def get_current_user(security_scopes: SecurityScopes,
                     token: Annotated[str, Depends(oauth2_scheme)],
                     authservice: AuthService = Depends(AuthService)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"

    with logfire.span("Verifying token"):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise InvalidCredentialsException({"WWW-Authenticate": authenticate_value})
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(scopes=token_scopes, username=username)
            logfire.info(f"Token verified successfully; scopes: {token_scopes}")
        except (InvalidTokenError, ValidationError) as e:
            logfire.error(f"Error while verifying token: {e}")
            raise InvalidCredentialsException({"WWW-Authenticate": authenticate_value})

        user = authservice.get_login_by_username(token_data.username)
        if user is None:
            raise InvalidCredentialsException({"WWW-Authenticate": authenticate_value})

        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise InvalidCredentialsException({"WWW-Authenticate": authenticate_value})
        return user


def get_current_valid_user(current_user: Login = Security(get_current_user, scopes=["user:read", "user:write"])):
    if not current_user.active:
        raise InactiveUserException
    return current_user
