from sqlalchemy import (Boolean, Column, Date, DateTime, Enum, ForeignKey,
                        Integer, String, func)
from sqlalchemy.orm import relationship

from db_config.sqlalchemy_connect import Base, engine


class Signup(Base):
    __tablename__ = 'signup'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False, unique=True)
    username = Column('username', String, unique=True, nullable=False, index=True)
    password = Column('password', String, nullable=False)
    email = Column('email', String, nullable=True, unique=True)
    phone = Column('phone', String, nullable=False, unique=True)
    created_at = Column('created_at', DateTime(timezone=True), server_default=func.now())


class Login(Base):
    __tablename__ = 'login'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False, unique=True)
    username = Column('username', String, unique=True, nullable=False, index=True)
    password = Column('password', String, nullable=False)
    email = Column('email', String, nullable=True, unique=True)
    phone = Column('phone', String, nullable=False, unique=True)
    active = Column('active', Boolean, nullable=False, default=True)
    created_at = Column('created_at', DateTime(timezone=True), server_default=func.now())
    registered_at = Column('registered_at', DateTime(timezone=True), server_default=func.now())

    profiles = relationship('Profile', back_populates='login')
    permission_sets = relationship('PermissionSet', back_populates='login')


class Permission(Base):
    __tablename__ = "permission"
    id = Column(Integer, primary_key=True, index=True, )
    name = Column(String, unique=True, index=False)
    description = Column(String, unique=False, index=False)

    permission_sets = relationship('PermissionSet', back_populates="permission")


class PermissionSet(Base):
    __tablename__ = "permission_set"
    id = Column(Integer, primary_key=True, index=True)
    login_id = Column(Integer, ForeignKey('login.id'), unique=False, index=False)
    permission_id = Column(Integer, ForeignKey('permission.id'), unique=False, index=False)

    login = relationship('Login', back_populates="permission_sets")
    permission = relationship('Permission', back_populates="permission_sets")


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False, unique=True)
    firstname = Column('firstname', String, nullable=False)
    lastname = Column('lastname', String, nullable=False)
    birthday = Column('birthday', Date, nullable=False)
    gender = Column('gender', Enum('male', 'female', name='genders'), nullable=False)
    created_at = Column('created_at', DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('login.id', ondelete="CASCADE"), nullable=False)

    login = relationship('Login', back_populates='profiles')


Base.metadata.create_all(engine)
