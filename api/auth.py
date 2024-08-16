from datetime import timedelta
from typing import Optional, Annotated
from uuid import UUID

import logfire
from fastapi import APIRouter, Cookie, Response, status, Depends, Form, \
    Security
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from starlette.responses import JSONResponse

from dependencies.auth import check_credential_error
from handler_exception import (InvalidCredentialsException,
                               UserNotFoundException,
                               CustomBadGatewayException)
from models.data.users import Login
from models.request.token import Token
from models.request.users import PendingUser, ValidUser, SignupCreate, \
    PasswordReset
from security.secure import authenticate, get_password_hash, \
                            get_current_valid_user, create_access_token, \
                            ACCESS_TOKEN_EXPIRE_MINUTES
from service.auth import AuthService

router = APIRouter(dependencies=[Depends(check_credential_error)])


# LOGIN
@router.post("/login")
@logfire.instrument('Login with username {uname}')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                authservice: AuthService = Depends(AuthService)) -> Token:

    try:
        account = authservice.get_login_by_username(form_data.username.lower())
    except UserNotFoundException:
        raise InvalidCredentialsException()

    if authenticate(form_data.password, account):
        # Extract the user's permissions and give them to the form data
        # erasing the ones sent by the client
        form_data.scopes = authservice.get_user_permissions(form_data.username.lower())
        authservice.verify_scopes(form_data.scopes, account.username)
        access_token = create_access_token(
            data={"sub": form_data.username.lower(), "scopes": form_data.scopes},
            expires_after=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return Token(access_token=access_token, token_type="bearer")
    else:
        raise InvalidCredentialsException()


@router.get("/login/me", response_model=ValidUser, status_code=status.HTTP_200_OK)
async def get_current_user(current_user: Login = Depends(get_current_valid_user)):
    return current_user


# CREATE A USER
@router.post('/login/signup', status_code=status.HTTP_201_CREATED, response_model=PendingUser)
@logfire.instrument('Signup with username {username}')
def signup(username: str = Form(...),
           password: str = Form(...),
           email: str = Form(...),
           phone: str = Form(...),
           authservice: AuthService = Depends(AuthService)):
    try:
        user = SignupCreate(
            username=username.lower(),
            password=password,
            email=email,
            phone=phone
        )
    except ValidationError as e:
        raise CustomBadGatewayException(detail=str(e))

    user.password = get_password_hash(user.password)
    result = authservice.signup(user)
    logfire.info("Signup successful")
    return result


# # APPROVE USER
@router.post("/login/validate", status_code=status.HTTP_201_CREATED, response_model=ValidUser)
@logfire.instrument('Validate username {uname}')
def approve_user(uname: str, authservice=Depends(AuthService)):
    uname = uname.lower()
    return authservice.validate_user(uname)


@router.get("/list/users/pending", status_code=status.HTTP_200_OK, response_model=list[PendingUser])
@logfire.instrument('List pending users')
async def list_pending_users(authservice=Depends(AuthService)):
    return authservice.get_all_signups()


@router.get("/list/users/valid", status_code=status.HTTP_200_OK, response_model=list[ValidUser])
@logfire.instrument('List valid users')
async def list_valid_users(authservice=Depends(AuthService)):
    return authservice.list_valid_users()


@router.delete("/delete/user/pending", status_code=status.HTTP_200_OK)
@logfire.instrument('Delete pending user {uname}')
def delete_pending_user(uname: str, authservice=Depends(AuthService),
                        current_user: Login = Security(get_current_valid_user)):
    if authservice.delete_signup(uname):
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Deleted successfully"})
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Something went wrong"})


@router.delete("/delete/user/valid")
@logfire.instrument('Delete valid user {uname}')
def delete_valid_user(uname: str, authservice=Depends(AuthService),
                      current_user: Login = Security(get_current_valid_user, scopes=["admin:read", "admin:write"])):
    if authservice.delete_valid_user(uname):
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Deleted successfully"})
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Something went wrong"})


# # CHANGE USERNAME
@router.patch("/login/password/change", status_code=status.HTTP_200_OK)
@logfire.instrument('Change password for user {current_user.username}')
def change_password(old_password: str = Form(...),
                    new_password: str = Form(...),
                    authservice: AuthService = Depends(AuthService),
                    current_user: Login = Security(get_current_valid_user)):
    try:
        passwords = PasswordReset(
            old_password=old_password,
            new_password=new_password
        )
    except CustomBadGatewayException as e:
        raise CustomBadGatewayException(detail=str(e))

    passwords.new_password = get_password_hash(new_password)

    if not authenticate(passwords.old_password, current_user):
        raise InvalidCredentialsException()

    if authservice.change_user_password(current_user.id, passwords.new_password):
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Password change successful"})
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Something went wrong"})


# CREATE COOKIE TO REMEMBER USER
@router.post("/login/rememberme/create", status_code=status.HTTP_200_OK)
def create_cookies(resp: Response, identity: UUID, username: str):
    resp.set_cookie(key="identity", value=str(identity))
    resp.set_cookie(key="username", value=username)
    return {"message": "cookies created successfully"}


# READ COOKIES TO REMEMBER USER
@router.get("/login/rememberme/read", status_code=status.HTTP_200_OK)
def read_cookies(username: Optional[str] = Cookie(None), identity: Optional[str] = Cookie(None)):
    return {"username": username, "identity": identity}
