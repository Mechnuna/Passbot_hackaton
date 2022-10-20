from sqlalchemy import func, and_, or_, text
from sqlalchemy.engine import Engine
from adatabaselib.crud.base import TableCRUD
from db.tables import table_entry_request
from models.entry_request import EntryRequestBaseModel
from typing import Optional, Union
from datetime import date
from models.enums import Campuses


class EntryRequestCRUD(TableCRUD):
    """
    Класс для работы с таблицей EntryRequest

    -------
    Methods:
        -	CREATE:
            -
            - 
            - 
        - 	UPDATE:
            - 
            -
            -
        -	SELECT:
            - count_by_names()
            - count_entry_requests_by_model()
            - 
        -	DELETE:
            -
            -
            -
    """

    def __init__(self, engine: Engine, schema=None):
        super().__init__(engine, table_entry_request, schema)
    
    
    def query_where_clause_er_universal(
        self,
        id_val: Optional[str] = None,
        ticket: Optional[str] = None,
        booking_date: Optional[date] = None,
        statuses: Optional[list] = None,
        initiator_name: Optional[str] = None,
        tg_name: Optional[str]=None,
        campus: Optional[Campuses] = None,
        responsible_nick: Optional[str] = None,
        is_active: Optional[int] = None,
        slice_date_start: Optional[date] = None,
        slice_date_end: Optional[date] = None
        ):
        """
        Генерит квери для where условий (AND)
        """

        where_clause = None
        where_list = []
        if id_val:
            where_list.append(self.table.c.ID == id_val)
        if ticket:
            where_list.append(self.table.c.TICKET == ticket)
        if booking_date:
            where_list.append(self.table.c.BOOKING_DATE == booking_date)
        if statuses:
            status_list = [self.table.c.STATUS == status for status in statuses]
            where_list.append(or_(*status_list))
        if initiator_name:
            where_list.append(self.table.c.INITIATOR_NAME == initiator_name)
        if tg_name:
            where_list.append(self.table.c.TG_NAME == tg_name)
        if responsible_nick:
            where_list.append(self.table.c.RESPONSIBLE_NICK == responsible_nick)
        if campus:
            where_list.append(self.table.c.CAMPUS == campus)
        if is_active:
            where_list.append(self.table.c.IS_ACTUAL == is_active)

        if slice_date_start:
            where_list.append(self.table.c.BOOKING_DATE >= slice_date_start)
        if slice_date_end:
            where_list.append(self.table.c.BOOKING_DATE <= slice_date_end)
    
        if where_list:
            where_clause = and_(*where_list)
        return where_clause
    
    def query_create_entry_request(self, er_model: EntryRequestBaseModel):
        query = self.table.insert().values(**er_model.dict())
        return query

    def query_basic_count_entry_request(self, where_clause = None):
        select_clause = func.count(self.table.c.TICKET)
        return self.query_basic_select(select_clause=select_clause, where_clause=where_clause)
    
    def query_count_by_names(
        self,
        tg_name: Optional[str] = None,
        initiator_name: Optional[str] = None,
        responsible_nick: Optional[str] = None,
        is_actual = 1,
        statuses: Optional[list] = None):

        where_clause = self.create_where_clause(
            [
                {
                    "column": self.table.c.TG_NAME,
                    "argument": tg_name
                },
                {
                    "column": self.table.c.INITIATOR_NAME,
                    "argument": responsible_nick
                },
                {
                    "column": self.table.c.TG_NAME,
                    "argument": initiator_name
                },
                {
                    "column": self.table.c.IS_ACTUAL,
                    "argument": is_actual
                },
                {
                    "column": self.table.c.STATUS,
                    "argument": statuses,
                    "method": "or"
                },
            ]
        )
        if where_clause is None:
            return None
        return self.query_basic_count_entry_request(where_clause=where_clause)

    
    def count_by_names(
        self,
        tg_name: Optional[str] = None,
        initiator_name: Optional[str] = None,
        responsible_nick: Optional[str] = None,
        is_actual = 1,
        statuses: Optional[list] = None):
        query = self.query_count_by_names(
            tg_name=tg_name,
            initiator_name=initiator_name,
            responsible_nick=responsible_nick,
            is_actual=is_actual,
            statuses=statuses
        )
        if query is None:
            return 0
        
        return self.execute_scalar(query=query)

    def count_er_universal(self,
        id_val: Optional[str] = None,
        ticket: Optional[str] = None,
        booking_date: Optional[date] = None,
        statuses: Optional[list] = None,
        initiator_name: Optional[str] = None,
        tg_name: Optional[str]=None,
        campus: Optional[Campuses] = None,
        responsible_nick: Optional[str] = None,
        is_active: Optional[int] = None,
        slice_date_start: Optional[date] = None,
        slice_date_end: Optional[date] = None):
        
        select_query = func.count(self.table.c.TICKET)
        where_clause = self.query_where_clause_er_universal(
            id_val=id_val,
            ticket=ticket,
            booking_date=booking_date,
            statuses=statuses,
            initiator_name=initiator_name,
            tg_name=tg_name,
            campus=campus,
            responsible_nick=responsible_nick,
            is_active=is_active,
            slice_date_start=slice_date_start,
            slice_date_end=slice_date_end
        )
        query = self.query_basic_select(
            select_clause=select_query,
            where_clause=where_clause)
        return self.fetchall(query=query)

    def select_er_dates_and_counts_by_names(self,
        tg_name: Optional[str]=None,
        statuses: Optional[list] = None,
        initiator_name: Optional[str] = None,
        responsible_nick: Optional[str] = None,
        slice_date_start: Optional[date] = None,
        slice_date_end: Optional[date] = None):


        alias_name = "BOOKED_N"
        select_query = ( self.table.c.BOOKING_DATE, text(f"COUNT(*) as {alias_name}"))
        where_clause = self.query_where_clause_er_universal(
            tg_name=tg_name,
            statuses=statuses,
            initiator_name=initiator_name,
            responsible_nick=responsible_nick,
            slice_date_start=slice_date_start,
            slice_date_end=slice_date_end
        )
        query = self.query_basic_select(
            select_clause=select_query, where_clause=where_clause).group_by(self.table.c.BOOKING_DATE)
        return self.fetchall(query=query)

    def create_entry_request(self, er_model: EntryRequestBaseModel):
        is_ok = True
        query = self.query_create_entry_request(er_model=er_model)
        try:
            self.execute(query=query)
        except Exception as e:
            print(e)
            is_ok = False
        
        return is_ok

    def query_select_by_tg(self, tg_name: str):
        query = self.table.select().where(self.table.c.TG_NAME == tg_name)
        return query

    def select_by_tg(self, tg_name: str):
        return self.fetchall(self.query_select_by_tg(tg_name=tg_name))


    def query_select_er_universal(
        self,
        id_val: Optional[str] = None,
        ticket: Optional[str] = None,
        booking_date: Optional[date] = None, 
        statuses: Optional[list] = None,
        initiator_name: Optional[str] = None,
        tg_name: Optional[str]=None,
        campus: Optional[Campuses] = None,
        responsible_nick: Optional[str] = None,
        is_active: Optional[int] = None,
        slice_date_start: Optional[date] = None,
        slice_date_end: Optional[date] = None):
        
        where_clause = self.query_where_clause_er_universal(
            id_val=id_val,
            ticket=ticket,
            booking_date=booking_date,
            statuses=statuses,
            initiator_name=initiator_name,
            tg_name=tg_name,
            campus=campus,
            responsible_nick=responsible_nick,
            is_active=is_active,
            slice_date_start=slice_date_start,
            slice_date_end=slice_date_end
        )
        if where_clause is not None:
            return self.table.select().where(where_clause)
        else:
            return None

    def select_by_booking_date(self, booking_date: date):
        query = self.query_select_er_universal(booking_date=booking_date)
        return self.fetchall(query)

    def select_er_universal(
        self,
        id_val: Optional[str] = None,
        ticket: Optional[str] = None,
        booking_date: Optional[date] = None, 
        statuses: Optional[list] = None,
        initiator_name: Optional[str] = None,
        tg_name: Optional[str]=None,
        campus: Optional[Campuses] = None,
        responsible_nick: Optional[str] = None,
        is_active: Optional[int] = None,
        slice_date_start: Optional[date] = None,
        slice_date_end: Optional[date] = None):

        query = self.query_select_er_universal(
            id_val=id_val,
            ticket=ticket,
            booking_date=booking_date,
            statuses=statuses,
            initiator_name=initiator_name,
            tg_name=tg_name,
            campus=campus,
            responsible_nick=responsible_nick,
            is_active=is_active,
            slice_date_start=slice_date_start,
            slice_date_end=slice_date_end
        )
        return self.fetchall(query)
    
    @TableCRUD.decorator_connection_session
    def update_universal(
        self,
        er_model: Union[EntryRequestBaseModel, dict],
        id_val: Optional[str] = None,
        ticket: Optional[str] = None,
        booking_date: Optional[date] = None, 
        statuses: Optional[list] = None,
        initiator_name: Optional[str] = None,
        tg_name: Optional[str]=None,
        campus: Optional[Campuses] = None,
        responsible_nick: Optional[str] = None,
        is_active: Optional[int] = None,
        slice_date_start: Optional[date] = None,
        slice_date_end: Optional[date] = None,
        connection=None):

        res = True
        where_clause = self.query_where_clause_er_universal(
            id_val=id_val,
            ticket=ticket,
            booking_date=booking_date,
            statuses=statuses,
            initiator_name=initiator_name,
            tg_name=tg_name,
            campus=campus,
            responsible_nick=responsible_nick,
            is_active=is_active,
            slice_date_start=slice_date_start,
            slice_date_end=slice_date_end
        )
        try:
            select_for_update = self.query_basic_select_for_update(
                table_to_select=self.table,
                where_clause=where_clause,
                of_column="STATUS")
            res_ex = connection.execute(select_for_update).fetchone()
            
        except Exception as e:
            print(e)
            res = False
        else:
            if res_ex:
                if isinstance(er_model, EntryRequestBaseModel):
                    query = self.table.update().values(**er_model.dict()).where(where_clause)
                else:
                    query = self.table.update().values(**er_model).where(where_clause)
                connection.execute(query)
        return res
