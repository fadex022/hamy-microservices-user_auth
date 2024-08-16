from typing import Dict, List, Any

import logfire
from fastapi import Depends
from sqlalchemy.orm import Session
from models.data.users import Profile, Login
from db_config.sqlalchemy_connect import SessionFactory, sess_db
from sqlalchemy import desc


class ProfileRepository:
    def __init__(self, sess: Session = Depends(sess_db)):
        self.sess: Session = sess

    def insert_profile(self, profile: Profile) -> bool:
        with logfire.span("Database Query: Inserting profile"):
            try:
                self.sess.add(profile)
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Error in profile repository with ProfileRepository.insert_profile: {e}")
                return False
        return True

    def get_profile_by_user_id(self, user_id: int) -> Profile:
        return self.sess.query(Profile).filter(Profile.user_id == user_id).first()

    def get_profile_by_id(self, profile_id: int) -> Profile:
        return self.sess.query(Profile).filter(Profile.id == profile_id).first()

    def delete_profile(self, profile_id: int) -> bool:
        with logfire.span("Database Query: Deleting profile"):
            try:
                self.sess.query(Profile).filter(Profile.id == profile_id).delete()
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Error in profile repository with ProfileRepository.delete_profile: {e}")
                return False
        return True

    def update_profile(self, profile_id: int, details: Dict[str, Any]) -> bool:
        with logfire.span("Database Query: Updating profile"):
            try:
                self.sess.query(Profile).filter(Profile.id == profile_id).update(details)
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Error in profile repository with ProfileRepository.update_profile: {e}")
                return False
        return True

    def get_all_profiles(self) -> List[Profile]:
        return self.sess.query(Profile).all()

    def join_profile_login(self) -> bool:
        return self.sess.query(Login, Profile).filter(Login.id == Profile.id).all()
