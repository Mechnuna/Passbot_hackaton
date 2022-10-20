from adatabaselib.crud.base import TableCRUD
from db.tables import table_authorized_users
from models.authorized_users import AuthorizedUsersBaseModel
from typing import Optional
from models.enums import ExecCodes



class AuthorizedUserCRUD(TableCRUD):
	def __init__(self, engine, schema=None):
		super().__init__(engine, table_authorized_users, schema)

	def query_select_by_names(self, tg_name: Optional[str] = None, resp_nick: Optional[str] = None):
		param_list = [
			{
				'column': self.table.c.TG_NAME,
				'argument': tg_name
			},
			{
				'column': self.table.c.RESPONSIBLE_NICK,
				'argument': resp_nick
			}]
		where_clause = self.create_where_clause(param_list)
		if where_clause is None:
			return None
		query = self.table.select().where(where_clause)
		return query
	
	def query_create_new_user(self, auth_user_model: AuthorizedUsersBaseModel):
		query = self.table.insert().values(**auth_user_model.dict())
		return query
	
	def query_update_invited(self, resp_nick: str, new_n_invited: int):
		query = self.table.update().values(CURRENT_INVITED = new_n_invited).where(
			self.table.c.RESPONSIBLE_NICK == resp_nick
		)
		return query

	def query_delete_user_by_nick(self, resp_nick: str):
		query = self.table.delete().where(self.table.c.RESPONSIBLE_NICK == resp_nick)
		return query

	def query_delete_user_by_tg_name(self, tg_name: str):
		query = self.table.delete().where(self.table.c.TG_NAME == tg_name)
		return query
	
	def select_by_names(self, tg_name: Optional[str] = None, resp_nick: Optional[str] = None):
		query = self.query_select_by_names(tg_name=tg_name, resp_nick=resp_nick)
		
		if query is None:
			return None
		return self.fetchall(query)

	def create_new_user(self, auth_user_model: AuthorizedUsersBaseModel):
		return self.execute(self.query_create_new_user(auth_user_model=auth_user_model))



	@TableCRUD.decorator_connection_session
	def update_user_by_model(
		self,
		auth_user_model: AuthorizedUsersBaseModel,
		of_column: str,
		where_clause,
		connection = None):
		try:
			query_select_for_update = self.query_select_this_table_for_update(
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
				connection.execute(self.query_update_this_table_by_model(
					dict_model=auth_user_model,
					where_clause=where_clause))
			except Exception as e:
				print(e)
			return ExecCodes.success


	def create_or_update_user(self, auth_user_model: AuthorizedUsersBaseModel):
		nick = auth_user_model.RESPONSIBLE_NICK
		res = self.select_by_names(resp_nick=nick)
		try:
			if not res:
				self.create_new_user(auth_user_model=auth_user_model)
			else:
				self.update_user_by_model(
					auth_user_model=auth_user_model,
					of_column="TG_NAME",
					where_clause=(self.table.c.RESPONSIBLE_NICK == nick))
		except Exception as e:
			print(e)
			return ExecCodes.failed
		
		return ExecCodes.success

	
	@TableCRUD.decorator_connection_session
	def update_invited(self, resp_nick: str, old_n: int, new_n: int, connection = None):
		try:
			query_select_for_update = self.query_basic_select_for_update(
				self.table, where_clause=(self.table.c.RESPONSIBLE_NICK == resp_nick),
				of_column="CURRENT_INVITED")
			pre_res = connection.execute(query_select_for_update).fetchone()
		except Exception as e:
			print(e)
		else:
			if pre_res is not None:
				if pre_res.CURRENT_INVITED != old_n:
					return False
				connection.execute(self.query_update_invited(resp_nick=resp_nick, new_n_invited=new_n))
		return True


	def delete_user_by_nick(self, resp_nick: str):
		try:
			self.execute(query=self.query_delete_user_by_nick(resp_nick=resp_nick))
		except Exception as e:
			print(e)
			return ExecCodes.failed
		return ExecCodes.success
	
	def delete_user_by_tg_name(self, tg_name: str):
		try:
			self.execute(query=self.query_delete_user_by_tg_name(tg_name=tg_name))
		except Exception as e:
			print(e)
			return ExecCodes.failed
		return ExecCodes.success
