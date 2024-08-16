from fastapi import Depends

from models.data.users import Profile
# from repository.factory import get_profile_repository
from repository.profile import ProfileRepository
from typing import List, Any, Dict


class ProfileService:
    def __init__(self, repo: ProfileRepository = Depends(ProfileRepository)):
        self.repo = repo

    def get_profile_by_user_id(self, user_id: int):
        return self.repo.get_profile_by_user_id(user_id)

    def get_profiles(self):
        return self.repo.get_all_profiles()

    def update_profile(self, profile_id: int, details: Dict[str, Any]):
        return self.repo.update_profile(profile_id, details)

    def create_profile(self, profile: Profile):
        profile = self.repo.get_profile_by_user_id(profile.user_id)
        if profile:
            return False
        else:
            return self.repo.insert_profile(profile)

    def delete_profile(self, profile_id: int):
        return self.repo.delete_profile(profile_id)
