from pydantic import BaseModel, Field
from models.enums import Roles, Campuses
from typing import Optional


class AuthorizedUsersBaseModel(BaseModel):
    RESPONSIBLE_NICK: str = Field(max_length=20)
    TG_NAME: str = Field(max_length=50)
    CAMPUS: Campuses
    INITIATOR_NAME: str
    ROLE: Roles
    CURRENT_INVITED: int = 0
    BLOCK_OPERATIONS: bool = False

    class Config:
        use_enum_values = True
