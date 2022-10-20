import unittest
from db.base import ENGINE
from crud.auth_tickets import AuthTicketsCRUD
from models.auth_tickets import AuthTicketsBaseModel
from models.enums import Campuses

auth_crud = AuthTicketsCRUD(ENGINE)
at_1 = AuthTicketsBaseModel(
	TG_NAME="Madabay",
	CAMPUS=Campuses.MOS,
	INITIATOR_NAME='LEONID',
	TICKET="909231")

at_2 = AuthTicketsBaseModel(
	TG_NAME="Madabay",
	CAMPUS=Campuses.MOS,
	INITIATOR_NAME='LEONID2')

at_3 = AuthTicketsBaseModel(
	TG_NAME="Madabay3",
	CAMPUS=Campuses.NSK,
	INITIATOR_NAME='LEONID3')

at_5 = AuthTicketsBaseModel(
	TG_NAME="Madabay4",
	CAMPUS=Campuses.KZN,
	INITIATOR_NAME='LEONID4')


class TestAuthTickets(unittest.TestCase):
	def test_create_new_auth_ticket(self):
		auth_crud.create_or_update_auth_ticket(at_1)
		auth_crud.create_or_update_auth_ticket(at_2)
		res_1 = auth_crud.select_auth_ticket_by_name(tg_name=at_1.TG_NAME)
		res_1 = AuthTicketsBaseModel.parse_obj(res_1)
		self.assertEqual(res_1.TG_NAME, at_1.TG_NAME)
		self.assertNotEqual(res_1.INITIATOR_NAME, at_1.INITIATOR_NAME)

	def test_select_auth_ticket(self):
		res_1 = auth_crud.select_auth_ticket_by_name("Somehing not")
		self.assertEqual(res_1, None)
