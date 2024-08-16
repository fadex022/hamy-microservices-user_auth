from typing import Type

import logfire
from fastapi import HTTPException, status, Depends

from handler_exception import (InvalidCredentialsException,
                               UserNotFoundException,
                               UserAlreadyExistsException,
                               UserNotValidException, EmailAlreadyUsedException, PhoneAlreadyUsedException)
from models.data.users import Signup, Login
from models.request.users import SignupCreate
from repository.auth import AuthRepository

active_users = logfire.metric_up_down_counter(
    'active_users',
    unit='1',
    description='Number of active users'
)


class AuthService:
    def __init__(self, repo: AuthRepository = Depends(AuthRepository)):
        self.repo = repo

    def login(self, username: str, password: str) -> Login:
        active_users.add(1)
        username = username.lower()
        user = self.repo.get_login_by_username_and_password(username, password)
        if not user:
            raise InvalidCredentialsException()
        else:
            return user

    def check_email(self, email: str) -> bool:
        signup = self.repo.get_signup_by_email(email)
        login = self.repo.get_login_by_email(email)
        if signup or login:
            return True
        else:
            return False

    def check_phone(self, phone: str) -> bool:
        signup = self.repo.get_signup_by_phone(phone)
        login = self.repo.get_login_by_phone(phone)
        if signup or login:
            return True
        else:
            return False

    def signup(self, user: SignupCreate) -> Signup:
        user_pending = self.repo.get_signup_by_username(user.username)
        if user_pending:
            raise UserNotValidException()

        user_valid = self.repo.get_login_by_username(user.username)
        if user_valid:
            raise UserAlreadyExistsException()

        if self.check_email(user.email):
            raise EmailAlreadyUsedException()

        if self.check_phone(user.phone):
            raise PhoneAlreadyUsedException()

        result = self.repo.insert_signup(user)

        if result:
            return self.repo.get_signup_by_username(user.username)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while signing up")

    def validate_user(self, username: str) -> Login:
        signup = self.repo.get_signup_by_username(username.lower())
        if not signup:
            raise UserNotFoundException()

        login = self.repo.get_login_by_username(username)
        if login:
            raise UserAlreadyExistsException()

        login = Login(username=signup.username, password=signup.password,
                      registered_at=signup.created_at, email=signup.email, phone=signup.phone)

        result = self.repo.insert_login(login)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while validating user")

        login = self.repo.get_login_by_username(login.username)
        self.repo.delete_signup(signup.username)

        # Giving roles to the new validated user
        for perm in ["user:read", "user:write"]:
            user_permission = self.repo.get_permission_by_name(perm)
            if login and user_permission:
                self.repo.insert_permission_set(user_permission.id, login.id)
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Error while validating user")

        return login

    def get_all_signups(self) -> list[Type[Signup]]:
        return self.repo.get_all_signup()

    def delete_signup(self, uname: str) -> bool:
        signup = self.repo.get_signup_by_username(uname)
        if not signup:
            raise UserNotFoundException()
        return self.repo.delete_signup(uname)

    def get_login_by_username(self, username: str) -> Login:
        login = self.repo.get_login_by_username(username)
        if not login:
            raise UserNotFoundException()
        return login

    def verify_scopes(self, scopes: list[str], username: str) -> None:
        user_id = self.repo.get_login_by_username(username).id
        for scope in scopes:
            scope_id = self.repo.get_permission_by_name(scope).id
            result = self.repo.get_permission_set(scope_id, user_id)
            if not result:
                logfire.instrument("Invalid scope")
                raise InvalidCredentialsException

    def get_user_permissions(self, username: str) -> list[str]:
        try:
            user_id = self.repo.get_login_by_username(username).id
        except Exception as e:
            logfire.error(f"Error while getting user permissions: {e}")
            raise UserNotFoundException

        permissions_set = self.repo.get_all_permission_set_by_user(user_id)
        permissions = []
        for permission_set in permissions_set:
            permission = self.repo.get_permission_by_id(permission_set.permission_id).name
            permissions.append(permission)
        return permissions

    def change_user_password(self, login_id: int, password: str) -> bool:
        details = {"password": password}
        if self.repo.get_login_by_id(login_id) is None:
            raise UserNotFoundException
        return self.repo.update_login(login_id, details)
