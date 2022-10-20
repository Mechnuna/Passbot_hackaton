from db.base import metadata, ENGINE
from db.tables import *
from db.auth_tickets import *

metadata.create_all(bind=ENGINE)
