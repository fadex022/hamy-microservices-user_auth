from pydantic_settings import BaseSettings
from datetime import date
import os


class AuthSettings(BaseSettings):
    application: str = 'Auth Management System'
    webmaster: str = 'bidigafadel@gmail.com'
    created: date = '2021-11-10'


class ServerSettings(BaseSettings):
    production_server: str
    prod_port: int
    development_server: str
    dev_port: int

    class Config:
        env_file = os.getcwd() + '/configuration/erp_settings.properties'


class DBSettings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    class Config:
        env_file = os.getcwd() + '/configuration/db_settings.properties'
