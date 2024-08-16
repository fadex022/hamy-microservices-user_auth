from datetime import date, datetime
import re
from pydantic import BaseModel, Field, EmailStr, ValidationError, field_validator


class SignupCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    email: EmailStr | None = Field(..., min_length=6)
    phone: str = Field(..., min_length=10, max_length=15)

    @field_validator('password')
    def password_complexity(cls, value: str) -> str:
        password_pattern = re.compile(
            r"""
            ^                # beginning of string
            (?=.*[A-Z])      # at least one uppercase letter
            (?=.*[a-z])      # at least one lowercase letter
            (?=.*\d)         # at least one digit
            (?=.*[!@#$%^&*()\-_=+]) # at least one special character
            .{8,}            # at least 8 characters long
            $                # end of string
            """, re.VERBOSE
        )

        if not password_pattern.match(value):
            raise ValueError(
                'Password must be at least 8 characters long, include an uppercase letter,\
                 a lowercase letter, a digit, and a special character.')

        return value

    class Config:
        from_attributes = True


class PasswordReset(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    def password_complexity(cls, value: str) -> str:
        password_pattern = re.compile(
            r"""
            ^                # beginning of string
            (?=.*[A-Z])      # at least one uppercase letter
            (?=.*[a-z])      # at least one lowercase letter
            (?=.*\d)         # at least one digit
            (?=.*[!@#$%^&*()\-_=+]) # at least one special character
            .{8,}            # at least 8 characters long
            $                # end of string
            """, re.VERBOSE
        )

        if not password_pattern.match(value):
            raise ValueError(
                'Password must be at least 8 characters long, include an uppercase letter,\
                 a lowercase letter, a digit, and a special character.')

        return value


class PendingUser(BaseModel):
    id: int = Field(..., ge=0)
    username: str = Field(..., min_length=3)
    email: EmailStr = Field(..., min_length=3)
    phone: str = Field(..., min_length=10, max_length=15)
    created_at: datetime

    class Config:
        from_attributes = True


class ValidUser(PendingUser):
    registered_at: datetime

    class Config:
        from_attributes = True


class ProfileOut(BaseModel):
    id: int
    firstname: str = Field(..., min_length=3)
    lastname: str = Field(..., min_length=3)
    birthday: date
    created_at: datetime
    login: ValidUser

    class Config:
        from_attributes = True
