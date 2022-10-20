#CRUDS:
from crud.entry_request import EntryRequestCRUD
from crud.authorized_users import AuthorizedUserCRUD
from crud.auth_tickets import AuthTicketsCRUD
#MODELS
from models.entry_request import EntryRequestBaseModel, EntryRequestCheckBox
from models.authorized_users import AuthorizedUsersBaseModel
from models.auth_tickets import AuthTicketsBaseModel
from models.enums import Campuses, AuthTicketStatuses, ExecCodes, Roles, EntryRequestStatuses
from models.roles import get_role
from datetime import date
from typing import Optional, Union

class Manager:
    """
    Класс для контроля над операциями с заявками
    """
    def __init__(self, engine) -> None:
        self.__engine = engine
        self.__entry_crud = EntryRequestCRUD(engine=self.__engine)
        self.__auth_user = AuthorizedUserCRUD(engine=self.__engine)
        self.__auth_tickets = AuthTicketsCRUD(engine=self.__engine)
    
# ---------------
    # AUTH_TICKETS:
    def update_auth_ticket_full_name(self, tg_name: str, full_name: str):
        auth_model = AuthTicketsBaseModel(TG_NAME=None, INITIATOR_NAME=full_name)
        auth_model.__delattr__("STATUS")
        res = self.__auth_tickets.update_auth_ticket_by_model(
            auth_model=auth_model,
            of_column="INITIATOR_NAME",
            where_clause=(self.__auth_tickets.table.c.TG_NAME == tg_name))
        return res

    def update_auth_ticket_campus(self, tg_name: str, campus: Campuses):
        auth_model = AuthTicketsBaseModel(TG_NAME=None, CAMPUS=campus)
        auth_model.__delattr__("STATUS")
        res = self.__auth_tickets.update_auth_ticket_by_model(
            auth_model=auth_model,
            of_column="INITIATOR_NAME",
            where_clause=(self.__auth_tickets.table.c.TG_NAME == tg_name))
        return res

    def update_auth_ticket_password(self, tg_name: str, password: str):
        auth_model = AuthTicketsBaseModel(TG_NAME=None, TICKET=password)
        auth_model.__delattr__("STATUS")
        res = self.__auth_tickets.update_auth_ticket_by_model(
            auth_model=auth_model,
            of_column="INITIATOR_NAME",
            where_clause=(self.__auth_tickets.table.c.TG_NAME == tg_name))
        return res
    
    def update_auth_ticket_nick(self, tg_name: str, nick: str):
        auth_model = AuthTicketsBaseModel(TG_NAME=None, RESPONSIBLE_NICK=nick)
        auth_model.__delattr__("STATUS")
        res = self.__auth_tickets.update_auth_ticket_by_model(
            auth_model=auth_model,
            of_column="INITIATOR_NAME",
            where_clause=(self.__auth_tickets.table.c.TG_NAME == tg_name))
        return res

    def update_auth_ticket_status(self, tg_name: str, status: AuthTicketStatuses):
        auth_model = AuthTicketsBaseModel(TG_NAME=None, STATUS=status)
        res = self.__auth_tickets.update_auth_ticket_by_model(
            auth_model=auth_model,
            of_column="INITIATOR_NAME",
            where_clause=(self.__auth_tickets.table.c.TG_NAME == tg_name))
        return res

    def select_auth_ticket_by_name(self, tg_name: str):
        pre_res = self.__auth_tickets.select_auth_ticket_by_name(tg_name=tg_name)
        if pre_res is None:
            return None
        res = AuthTicketsBaseModel.parse_obj(pre_res)
        return res

    def	create_new_auth_ticket(self, auth_model : AuthTicketsBaseModel) -> bool:
        try:
            exec_code = self.__auth_tickets.create_new_auth_ticket(auth_model)
        except Exception:
            exec_code = ExecCodes.failed
        return exec_code

    def create_new_auth_ticket_if_not_exists(self, auth_model : AuthTicketsBaseModel) -> bool:
        exec_code = self.__auth_tickets.create_or_update_auth_ticket(auth_model=auth_model)
        return exec_code
    
    def delete_auth_ticket_by_tg_name(self, tg_name: str):
        exec_code = self.__auth_tickets.delete_auth_ticket_by_tg_name(tg_name=tg_name)
        return exec_code

    def delete_auth_ticket_by_status(self, status: AuthTicketStatuses):
        exec_code = self.__auth_tickets.delete_auth_ticket_by_status(status=status)
        return exec_code 
# ---------------   
    # AUTH_USERS:
    def	select_auth_user_by_tg(self, tg_name : str):
        res = []
        pre_res = self.__auth_user.select_by_names(tg_name=tg_name)
        if pre_res is None or not pre_res:
            return None
        else:
            res = AuthorizedUsersBaseModel.parse_obj(pre_res[0])
            return res
    
    def	create_new_auth_user(self, auth_user_model: AuthorizedUsersBaseModel) -> bool:
        is_successful = True
        try:
            is_successful = self.__auth_user.create_new_user(auth_user_model)
        except Exception:
            is_successful = False
        return is_successful

    def create_new_auth_user_from_auth_tickets(self, tg_name: str, role = Roles.LEARNER.value) -> bool:
        try:
            auth_ticket = self.select_auth_ticket_by_name(tg_name=tg_name)
            if auth_ticket is None:
                return True
            auth_user_model = AuthorizedUsersBaseModel(
                RESPONSIBLE_NICK=auth_ticket.RESPONSIBLE_NICK,
                TG_NAME=auth_ticket.TG_NAME,
                CAMPUS=auth_ticket.CAMPUS,
                INITIATOR_NAME=auth_ticket.INITIATOR_NAME,
                ROLE=role,
            )
            res = self.create_new_auth_user(auth_user_model=auth_user_model)
        except Exception as e:
            print(e)
            return False
        else:
            return res
    
    def update_auth_user_invited_n(self, resp_nick: str, old_n: int, new_n: int):
        response = self.__auth_user.update_invited(resp_nick=resp_nick, old_n=old_n, new_n=new_n)
        return response

# ---------------  
    # ENTRY_REQUEST:
    def create_new_entry_request(self, er_model: EntryRequestBaseModel) -> bool:
        is_successful = True
        try:
            is_successful = self.__entry_crud.create_entry_request(er_model)
        except Exception:
            is_successful = False
        
        return is_successful


    def select_from_entry_request_by_tg(self, tg_name: str):
        res = []
        pre_res = self.__entry_crud.select_by_tg(tg_name=tg_name)
        if pre_res is None:
            return None
        else:
            res = [EntryRequestBaseModel.parse_obj(x) for x in pre_res]
            return res
    
    def __message_from_entry_request(self, can_create: bool, message: str, current_invited: int, role: str):
        er_box = EntryRequestCheckBox(
            CAN_CREATE=can_create,
            MESSAGE=message,
            CURRENT_INVITED=current_invited,
            ROLE=role
        )
        return er_box

    
    def check_if_entry_request_creatable(
        self,
        tg_name: str,
        role: Roles) -> EntryRequestCheckBox:
        
        
        role_owner = get_role(role)
        can_create = True
        message = ""
        current_invited = 0
        if role_owner.is_in_school:
            auth_user_model = self.select_auth_user_by_tg(tg_name=tg_name)
            if not auth_user_model:
                can_create = False
                message = "Юзер не найден по тг в базе авторизированных юзеров"
            else:
                if not role_owner.has_unlimited_booking and role_owner.max_people_to_book <= auth_user_model.CURRENT_INVITED:
                    can_create = False
                    message = f"У вас избыток активных приглашений. Максимум {role_owner.max_people_to_book}, у Вас - {auth_user_model.CURRENT_INVITED}"
                else:
                    can_create = True
                    message = "OK"
                current_invited = auth_user_model.CURRENT_INVITED
        else:
            requests_counted = self.__entry_crud.count_by_names(
                tg_name=tg_name,
                statuses=[EntryRequestStatuses.confirmed.value, EntryRequestStatuses.new.value]
            )
            if requests_counted == 0:
                message = "OK"
            else:
                can_create = False
                message = f"У вас избыток активных приглашений. Максимум 1, у Вас - {requests_counted}"
            current_invited = requests_counted
        
        return self.__message_from_entry_request(can_create=can_create, message=message, current_invited=current_invited, role=role)

    
    def create_entry_request_using_role(
        self,
        tg_name: str,
        er_model: EntryRequestBaseModel):
        
        auth_user = self.select_auth_user_by_tg(tg_name=tg_name)
        if auth_user:
            role = auth_user.ROLE
        else:
            role = Roles.OUTSIDER.value
        
        role_owner = get_role(role)
        if role_owner.is_in_school: # в контуре школы
            er_model = er_model
            er_model.RESPONSIBLE_NICK = auth_user.RESPONSIBLE_NICK
            er_model.CAMPUS = auth_user.CAMPUS
            er_model.RESPONSIBLE_NAME = auth_user.INITIATOR_NAME
            er_model.STATUS = EntryRequestStatuses.confirmed.value

            self.__auth_user.update_invited(
                resp_nick=auth_user.RESPONSIBLE_NICK,
                old_n=auth_user.CURRENT_INVITED,
                new_n=auth_user.CURRENT_INVITED + 1)
        
        is_ok = self.create_new_entry_request(er_model=er_model)
        return is_ok

    def select_entry_request_by_booking_date(self, booking_date: date):
        res = []
        res = self.__entry_crud.select_by_booking_date(booking_date)
        if res:
            return [EntryRequestBaseModel.parse_obj(elem) for elem in res]
        return None

    def select_entry_request_confirmed_by_booking_date(self, booking_date: date):
        res = []
        res = self.__entry_crud.select_er_universal(
            booking_date=booking_date,
            statuses=[EntryRequestStatuses.confirmed.value],
            is_active=1
        )
        if res:
           return [EntryRequestBaseModel.parse_obj(elem) for elem in res]
        return None
    
    def select_entry_request_status_new(self):
        res = []
        res = self.__entry_crud.select_er_universal(
            is_active=1,
            statuses=[EntryRequestStatuses.new.value]
        )
        if res:
           return [EntryRequestBaseModel.parse_obj(elem) for elem in res]
        return None

    def select_entry_request_by_tg_name(self, tg_name: str):
        res = []
        res = self.__entry_crud.select_er_universal(
            tg_name=tg_name,
            statuses=[EntryRequestStatuses.new.value, EntryRequestStatuses.confirmed.value, EntryRequestStatuses.rejected.value]
        )
        if res:
           return [EntryRequestBaseModel.parse_obj(elem) for elem in res]
        return None
    
    def update_entry_request_by_id(self, id_val: int, er_model: EntryRequestBaseModel):
        self.__entry_crud.update_universal(er_model=er_model, id_val=id_val)
        return None


    def select_er_overlimited_dates_and_counts_by_names(
        self,
        role: Roles,
        tg_name: Optional[str]=None,
        initiator_name: Optional[str] = None,
        responsible_nick: Optional[str] = None,
        slice_date_start: Optional[date] = None,
        slice_date_end: Optional[date] = None) -> dict:


        role_model = get_role(role)
        max_per_day = role_model.max_people_to_book
        if not role_model.has_unlimited_booking:
            res = self.__entry_crud.select_er_dates_and_counts_by_names(
                tg_name=tg_name,
                statuses=[EntryRequestStatuses.confirmed.value, EntryRequestStatuses.new.value],
                initiator_name=initiator_name,
                responsible_nick=responsible_nick,
                slice_date_start=slice_date_start,
                slice_date_end=slice_date_end
            )
            if not res:
                return {}
            pre_dict = dict(res)
            ret_dict = {}
            for k, v in pre_dict.items():
                if v >= max_per_day:
                    ret_dict.update({k:v})
            return ret_dict
        else:
            return {}
    
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

        res = self.__entry_crud.select_er_universal(
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
        if res:
            return [EntryRequestBaseModel.parse_obj(elem) for elem in res]
        return None

    def update_er_universal(self,
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
        slice_date_end: Optional[date] = None):

        exec_code = self.__entry_crud.update_universal(
            er_model=er_model,
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
            slice_date_end=slice_date_end)
        return exec_code

    def update_er_universal_status(self,
        new_status: EntryRequestStatuses,
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
        
        exec_code = self.update_er_universal(
            er_model={"STATUS":new_status},
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
            slice_date_end=slice_date_end)
        return exec_code
