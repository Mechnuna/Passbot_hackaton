from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Sequence
from db.base import metadata


table_entry_request = Table(
	"ENTRY_REQUEST",
	metadata,
	Column("ID", Integer, primary_key=True, autoincrement=True),
	Column('TICKET', String(32), nullable=False),
    Column('TG_NAME', String(50)),
    Column('INITIATOR_NAME', String(100)),
	Column('RESPONSIBLE_NICK', String(20)),
	Column('RESPONSIBLE_NAME', String(100)),
	Column('GUEST_NAME', String(100)),
	Column('GUEST_TYPE', String(50)),
	Column('CAMPUS', String(20)),
	Column('BOOKING_DATE', Date),
	Column('CREATION_DATE', DateTime),
	Column('UPDATE_DATE', DateTime),
    Column('STATUS', String(30)),
	Column('IS_ACTUAL', Integer, nullable = False)
)

table_authorized_users = Table(
	"AUTHORIZED_USERS",
	metadata,
	Column('RESPONSIBLE_NICK', String(20), primary_key=True),
	Column('TG_NAME', String(50), nullable = False),
    Column('INITIATOR_NAME', String(100), nullable = False),
	Column('CAMPUS', String(30), nullable = False),
	Column('ROLE', String(20), nullable = False),
	Column('CURRENT_INVITED', Integer, nullable = False),
	Column('BLOCK_OPERATIONS', Integer, nullable = False)
)

table_guests = Table(
	"GUESTS",
	metadata,
	Column('GUEST_NAME', String(100)),
	Column('ACTUAL_INVITATION', Integer),
	Column('BLOCK_GUEST', Integer)
)
