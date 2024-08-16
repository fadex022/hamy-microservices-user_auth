from typing import Any, Dict
from typing_extensions import Annotated, Doc
from fastapi import HTTPException


class InvalidCredentialsException(HTTPException):
    def __init__(self, headers: Dict[str, str] | None = None):
        super().__init__(status_code=401, detail="Invalid credentials", headers=headers)


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")


class InvalidPasswordException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid password")


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User already exists")


class UserNotValidException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="User in pending list")


class EmptyInputException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Input cannot be empty")


class CustomBadGatewayException(HTTPException):
    def __init__(self, status_code: int = 400, detail: str | None = None,
                 headers: Dict[str, str] | None = None) -> None:
        super().__init__(status_code, detail, headers)


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Token needed")


class SameUsernamePasswordException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Username and password cannot be the same")


class InactiveUserException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Inactive user")


class EmailAlreadyUsedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Email already used")


class PhoneAlreadyUsedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Phone number already used")
