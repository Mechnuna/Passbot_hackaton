from typing import Optional
from adatabaselib.crud.base import TableCRUD
from db.auth_tickets import table_auth_tickets
from models.auth_tickets import AuthTicketsBaseModel
from models.enums import ExecCodes, AuthTicketStatuses


class AuthTicketsCRUD(TableCRUD):
	def __init__(self, engine, schema=None):
		super().__init__(engine, table_auth_tickets, schema)
	
	def query_create_new_auth_ticket(self, auth_model: AuthTicketsBaseModel):
		query = self.table.insert().values(**auth_model.dict())
		return query

	def query_select_auth_ticket(self, where_clause):
		query = self.table.select().where(where_clause)
		return query
	
	def query_select_auth_ticket_by_name(self, tg_name: str):
		query = self.query_select_auth_ticket((self.table.c.TG_NAME == tg_name))
		return query

	def query_select_auth_ticket_for_update(
		self,
		of_column: str,
		where_clause):
		query = self.query_basic_select_for_update(
			table_to_select=self.table,
			where_clause=where_clause,
			of_column=of_column)
		return query

	def query_update_auth_ticket_by_model(self, auth_model: AuthTicketsBaseModel, where_clause):
		pre_dict = auth_model.dict()
		val_dict = self.filter_none_values(dict_to_filter=pre_dict)
		query = self.table.update().values(**val_dict).where(where_clause)
		return query

	def query_delete_auth_ticket_by_status(self, status: AuthTicketStatuses):
		query = self.table.delete().where(self.table.c.STATUS == status)
		return query
	

	def query_delete_auth_ticket_by_tg_name(self, tg_name: str):
		query = self.table.delete().where(self.table.c.TG_NAME == tg_name)
		return query
	
	def create_new_auth_ticket(self, auth_model: AuthTicketsBaseModel):
		try:
			self.execute(self.query_create_new_auth_ticket(auth_model=auth_model))
		except Exception as e:
			print(e) # ! Добавить логгирование
			return ExecCodes.failed
		else:
			return ExecCodes.success
	
	def select_auth_ticket_by_name(self, tg_name: str):
		try:
			res = self.fetchone(self.query_select_auth_ticket_by_name(tg_name=tg_name))
		except Exception as e:
			print(e)
			return None
		else:
			return res

	@TableCRUD.decorator_connection_session
	def update_auth_ticket_by_model(
		self,
		auth_model,
		of_column: str,
		where_clause,
		connection = None):
		try:
			query_select_for_update = self.query_select_auth_ticket_for_update(
				of_column=of_column,
				where_clause=where_clause)
			res = connection.execute(query_select_for_update).fetchone()
		except Exception as e:
			print(e)
			return ExecCodes.failed
		else:
			if res is None:
				return ExecCodes.failed
			try:
				connection.execute(self.query_update_auth_ticket_by_model(
					auth_model=auth_model,
					where_clause=where_clause))
			except Exception as e:
				print(e)
			return ExecCodes.success
	
	@TableCRUD.decorator_connection_session
	def delete_auth_ticket_by_tg_name(self, tg_name: str, connection = None):
		try:
			query_select_for_update = self.query_select_auth_ticket_for_update(
				of_column="STATUS",
				where_clause=(self.table.c.TG_NAME == tg_name))
			res = connection.execute(query_select_for_update).fetchone()
		except Exception as e:
			print(e)
			return ExecCodes.failed
		else:
			if res is None:
				return ExecCodes.failed
			connection.execute(self.query_delete_auth_ticket_by_tg_name(tg_name=tg_name))
			return ExecCodes.success

	@TableCRUD.decorator_connection_session
	def delete_auth_ticket_by_status(self, status: AuthTicketStatuses, connection = None):
		try:
			query_select_for_update = self.query_select_auth_ticket_for_update(
				of_column="STATUS",
				where_clause=(self.table.c.STATUS == status))
			res = connection.execute(query_select_for_update).fetchone()
		except Exception as e:
			print(e)
			return ExecCodes.failed
		else:
			if res is None:
				return ExecCodes.failed
			connection.execute(self.query_delete_auth_ticket_by_status(status=status))
			return ExecCodes.success

	def create_or_update_auth_ticket(self, auth_model: AuthTicketsBaseModel):
		tg_name = auth_model.TG_NAME
		res = self.select_auth_ticket_by_name(tg_name=tg_name)
		try:
			if res is None:
				self.create_new_auth_ticket(auth_model=auth_model)
			else:
				self.update_auth_ticket_by_model(
					auth_model=auth_model,
					of_column="STATUS",
					where_clause=(self.table.c.TG_NAME == tg_name))
		except Exception as e:
			print(e)
			return ExecCodes.failed
		
		return ExecCodes.success
