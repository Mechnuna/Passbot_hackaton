from enum import Enum, unique

@unique
class EntryRequestStatuses(Enum):
	new = "new"
	confirmed = "confirmed"
	rejected = "rejected"
	expired = "expired"

@unique
class AuthTicketStatuses(Enum):
	new = "new"
	confirmed = "confirmed"
	expired = "expired"

@unique
class Campuses(Enum):
	KZN = 'KZN'
	MOS = 'Moscow'
	NSK = 'NSK'

@unique
class Roles(Enum):
	STAFF = 'STAFF'
	ADM = 'ADM'
	LEARNER = 'LEARNER'
	ABITUR = 'ABITUR'
	OUTSIDER = 'OUTSIDER'


@unique
class ExecCodes(Enum):
	success = 1
	failed = 0
	error = -1
