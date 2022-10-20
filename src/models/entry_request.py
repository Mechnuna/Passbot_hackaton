from pydantic import BaseModel, Field
from adatabaselib.core.encrypt import get_uuid
from adatabaselib.core.utils import get_time
from datetime import datetime, date
from models.enums import Roles, EntryRequestStatuses, Campuses
from typing import Optional


class EntryRequestBaseModel(BaseModel):
    """
    """
    ID: int = None
    TICKET: str = Field(min_length=32, max_length=32, default_factory=get_uuid)
    
    TG_NAME: str = Field(max_length=50)
    INITIATOR_NAME: str = Field(max_length=60)
    
    RESPONSIBLE_NICK: Optional[str] = Field(None, max_length=30)
    RESPONSIBLE_NAME: Optional[str] = Field(None, max_length=60)
    GUEST_NAME: Optional[str] = Field(max_length=60)
    GUEST_TYPE: str = "default"
    CAMPUS: Optional[Campuses]
    BOOKING_DATE: Optional[date] = None
    CREATION_DATE: datetime = Field(default_factory=get_time)
    UPDATE_DATE: datetime = Field(default_factory=get_time)
    STATUS: EntryRequestStatuses = EntryRequestStatuses.new.value
    IS_ACTUAL: int = 1

    class Config:
        use_enum_values = True


class EntryRequestCheckBox(BaseModel):
    CAN_CREATE: bool
    MESSAGE: str
    CURRENT_INVITED: int
    ROLE: Roles

    class Config:
        use_enum_values = True

