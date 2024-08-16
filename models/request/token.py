from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Token:
    access_token: str
    token_type: str


@dataclass
class TokenData:
    username: Optional[str] = None
    scopes: list[str] = field(default_factory=list)
