from datetime import datetime
from typing import Any, Type

import logfire
from fastapi import Depends
from sqlalchemy.orm import Session
from db_config.sqlalchemy_connect import sess_db

from models.data.users import Signup, Login, PermissionSet, Permission
from sqlalchemy import desc, Row

from models.request.users import SignupCreate


class AuthRepository:
    def __init__(self, sess: Session = Depends(sess_db)):
        self.sess: Session = sess

    def insert_signup(self, user: SignupCreate) -> bool:
        with logfire.span("Database Query: Inserting signup"):
            try:
                self.sess.add(Signup(**user.dict()))
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Database query failed: {e}")
                return False
        return True

    def update_signup(self, signup_id: int, details: dict[str, Any]) -> bool:
        with logfire.span("Database Query: Updating signup"):
            try:
                self.sess.query(Signup).filter(Signup.id == signup_id).update(details)
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Database query failed: {e}")
                return False
        return True

    def delete_signup(self, uname: str) -> bool:
        with logfire.span("Database Query: Deleting signup"):
            try:
                self.sess.query(Signup).filter(Signup.username == uname).delete()
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Database query failed: {e}")
                return False
        return True

    def get_all_signup(self) -> list[Type[Signup]]:
        return self.sess.query(Signup).all()

    def get_signup_by_username(self, username: str) -> Signup | None:
        return self.sess.query(Signup).filter(Signup.username == username).one_or_none()

    def get_signup_by_email(self, email: str) -> Signup | None:
        return self.sess.query(Signup).filter(Signup.email == email).first()

    def get_signup_by_phone(self, phone: str) -> Signup | None:
        return self.sess.query(Signup).filter(Signup.phone == phone).first()

    def get_all_signup_sorted(self) -> list[Row[tuple[Any, Any, Any]]]:
        return self.sess.query(Signup.id, Signup.username, Signup.created_at) \
                    .order_by(desc(Signup.username)).all()

    def get_signup_by_id(self, signup_id: int) -> Signup:
        return self.sess.query(Signup).filter(Signup.id == signup_id).first()

    def insert_login(self, login: Login) -> bool:
        with logfire.span("Database Query: Inserting login"):
            try:
                self.sess.add(login)
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Database query failed: {e}")
                return False
        return True

    def update_login(self, login_id: int, details: dict[str, Any]) -> bool:
        with logfire.span("Database Query: Updating login"):
            try:
                self.sess.query(Login).filter(Login.id == login_id).update(details)
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Database query failed: {e}")
                return False
        return True

    def delete_login(self, login_id: int) -> bool:
        with logfire.span("Database Query: Deleting login"):
            try:
                self.sess.query(Login).filter(Login.id == login_id).delete()
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Database query failed: {e}")
                return False
        return True

    def get_login_by_username(self, username: str) -> Login:
        return self.sess.query(Login).filter(Login.username == username).first()

    def get_login_by_email(self, email: str) -> Login | None:
        return self.sess.query(Login).filter(Login.email == email).first()

    def get_login_by_phone(self, phone: str) -> Login | None:
        return self.sess.query(Login).filter(Login.phone == phone).first()

    def get_login_by_id(self, login_id: int) -> Login:
        return self.sess.query(Login).filter(Login.id == login_id).first()

    def get_all_login(self) -> list[Type[Login]]:
        return self.sess.query(Login).all()

    def get_login_by_username_and_password(self, username: str, password: str) -> Login:
        return self.sess.query(Login).filter(Login.username == username,
                                             Login.password == password).first()

    def get_permission_by_name(self, name: str) -> Permission:
        return self.sess.query(Permission).filter(Permission.name == name).first()

    def get_permission_by_id(self, permission_id: int) -> Permission:
        return self.sess.query(Permission).filter(Permission.id == permission_id).first()

    def insert_permission_set(self, permission_id: int, login_id: int) -> bool:
        with logfire.span("Database Query: Inserting permission set"):
            try:
                permission_set = PermissionSet(permission_id=permission_id, login_id=login_id)
                self.sess.add(permission_set)
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Database query failed: {e}")
                return False

    def delete_permission_set(self, permission_id: int, login_id: int) -> bool:
        with logfire.span("Database Query: Deleting permission set"):
            try:
                self.sess.query(PermissionSet).filter(PermissionSet.permission_id == permission_id,
                                                      PermissionSet.login_id == login_id).delete()
                self.sess.commit()
            except Exception as e:
                logfire.error(f"Database query failed: {e}")
                return False

    def get_permission_set(self, permission_id: int, login_id: int) -> PermissionSet:
        return self.sess.query(PermissionSet).filter(PermissionSet.permission_id == permission_id,
                                                      PermissionSet.login_id == login_id).first()

    def get_all_permission_set_by_user(self, user_id: int) -> list[PermissionSet]:
        return self.sess.query(PermissionSet).filter(PermissionSet.login_id == user_id).all()
