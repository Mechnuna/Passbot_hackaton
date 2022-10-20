from sqlalchemy import Table, Column, Integer, String, Date, DateTime
from db.base import metadata


table_auth_tickets = Table(
	"AUTH_TICKETS",
	metadata,
    Column('TG_NAME', String(50), primary_key=True, nullable=False),
    Column('CAMPUS', String(30), nullable = True),
    Column('RESPONSIBLE_NICK', String(20), nullable=True),
    Column('INITIATOR_NAME', String(100), nullable = True),
    Column('TICKET', String(10), nullable = True),
    Column('STATUS', String(30), nullable = False)
)
