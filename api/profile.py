from datetime import date

import logfire
from fastapi import APIRouter, Form, HTTPException, status, Depends, Security
from typing import Dict, Optional, Any
from uuid import UUID

from starlette.responses import JSONResponse

from handler_exception import UserNotFoundException, InvalidTokenException, CustomBadGatewayException

from models.data.classifications import UserType
from models.data.users import Profile, Login
from models.request.users import ProfileOut
from security.secure import get_current_valid_user
from service.profiles import ProfileService

router = APIRouter()


@router.post("/account/profile/add", status_code=status.HTTP_200_OK)
@logfire.instrument("Creating profile for user {current_user.username}")
def add_profile(fname: str = Form(...),
                lname: str = Form(...),
                bday: date = Form(...),
                gender: str = Form(...),
                current_user: Login = Depends(get_current_valid_user),
                profile_service: ProfileService = Depends(ProfileService)):
    profile = Profile(
        firstname=fname,
        lastname=lname,
        birthday=bday,
        gender=gender,
        user_id=current_user.id,
    )

    if profile_service.create_profile(profile):
        return profile_service.get_profile_by_user_id(current_user.id)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Something went wrong"})


@router.put("/account/profile/update", status_code=status.HTTP_200_OK)
@logfire.instrument("Updating profile for user {current_user.username}")
def update_profile(details: Dict[str, Any], current_user: Login = Depends(get_current_valid_user),
                   profile_service: ProfileService = Depends(ProfileService)):
    profile = profile_service.get_profile_by_user_id(current_user.id)
    if profile:
        if profile_service.update_profile(profile.id, details):
            return profile_service.get_profile_by_user_id(current_user.id)
        else:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                content={"message": "Something went wrong"})
    else:
        raise UserNotFoundException()


@router.delete("/account/profile/delete")
@logfire.instrument("Deleting profile for user {current_user.username}")
def delete_profile(profile_id: int, current_user: Login = Security(get_current_valid_user, scopes=['admin:write']),
                   profile_service: ProfileService = Depends(ProfileService)):
    if profile_service.delete_profile(profile_id):
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Profile deleted successfully"})
    else:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"message": "Something went wrong"})


@router.get("/account/profile/get", status_code=status.HTTP_200_OK, response_model=ProfileOut)
@logfire.instrument("Getting profile for user {current_user.username}")
def get_profile(current_user: Login = Depends(get_current_valid_user),
                profile_service: ProfileService = Depends(ProfileService)):
    return profile_service.get_profile_by_user_id(current_user.id)
