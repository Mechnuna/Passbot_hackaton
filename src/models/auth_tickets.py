from pydantic import BaseModel, Field
from models.enums import AuthTicketStatuses, Campuses

from typing import Optional



class AuthTicketsBaseModel(BaseModel):
    TG_NAME: Optional[str]
    TICKET: Optional[str] = None
    CAMPUS: Optional[Campuses] = None
    INITIATOR_NAME: Optional[str] = None
    RESPONSIBLE_NICK: Optional[str] = None
    STATUS: AuthTicketStatuses = AuthTicketStatuses.new.value

    class Config:
        use_enum_values = True
 