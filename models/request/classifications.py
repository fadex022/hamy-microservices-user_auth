from enum import Enum


class UserType(str, Enum):
    admin = "admin"
    client = "client"
    pharmacy = "pharmacy"
    deliveryman = "deliveryman"
