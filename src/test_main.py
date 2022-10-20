from ops.manager import Manager
from crud.authorized_users import AuthorizedUserCRUD
from crud.auth_tickets import AuthTicketsCRUD
from crud.entry_request import EntryRequestCRUD
from db.base import ENGINE
from models.entry_request import EntryRequestBaseModel
from models.authorized_users import AuthorizedUsersBaseModel
from models.auth_tickets import AuthTicketsBaseModel
from datetime import date
from models.enums import Campuses, EntryRequestStatuses, Roles, AuthTicketStatuses
manager = Manager(ENGINE)


# auth_crud = AuthorizedUserCRUD(engine=ENGINE)
my_date = date(2022, 3, 30)

er_model = EntryRequestBaseModel(
    TG_NAME="Mechuna",
    INITIATOR_NAME="Ким Мария",
    RESPONSIBLE_NAME="МС Алена",
    GUEST_NAME="Ким Мария",
    CAMPUS=Campuses.MOS.value,
    BOOKING_DATE=my_date
)

urs = AuthorizedUsersBaseModel(
    RESPONSIBLE_NICK= "sstyx",
    TG_NAME = "Mechnuna",
    CAMPUS= Campuses.MOS.value,
    INITIATOR_NAME = "Ким Мария",
    ROLE= Roles.LEARNER.value,
    CURRENT_INVITED=0,
    BLOCK_OPERATIONS = False,
)
# auth_user_model = AuthorizedUsersBaseModel(
#     RESPONSIBLE_NICK="droro",
#     TG_CONTACT="kim",
#     ROLE=Roles.ADM
# )
# auth_crud.create_new_user(auth_user_model)
# manager.create_entry_request_using_role("kim", er_model)
# # x = manager.select_from_entry_request_by_tg(tg_name="kim")
# print(manager.check_if_entry_request_creatable("kim", Roles.ADM.value))
# x = manager.select_entry_request_confirmed_by_booking_date(my_date)
# print(x)
print(manager.select_entry_request_by_tg_name(tg_name="234"))
manager.create_new_entry_request(er_model=er_model)

# manager.create_new_entry_request(er_model)
# x = manager.select_from_entry_request_by_tg(tg_name="kim")
# print(x)

# # auth_crud.create_new_user(auth_user_model)
# # y = auth_crud.select_by_tg(tg_name="kim")
# # print("ZZZ: ", y)
# auth_crud.update_invited(resp_nick="droro", increment=1)

# y = auth_crud.select_by_names(tg_name="kim", resp_nick="droro")
# print("NEW STATE: ", y)
# app = FastAPI()
# def 

# # Запуск приложения:
# if __name__=="__main__":
#     # Запуск приложения
    # uvicorn.run("xmain:app", port=3000, host="localhost", workers=1)

auth_tickets = AuthTicketsCRUD(engine=ENGINE)

atick_model = AuthTicketsBaseModel(
    TG_NAME="Mechnuna"
)
# manager.create_auth_new_auth_ticket_if_not_exists(
#     atick_model
# )
# # manager.create_auth_new_auth_ticket_if_not_exists(
# #     atick_model
# # )

manager.create_new_auth_user(urs)
s = manager.check_if_entry_request_creatable("Mechnuna", Roles.LEARNER.value)
print(s.CAN_CREATE)
q = manager.select_entry_request_status_new()
# print(q)
manager.create_new_entry_request(er_model=er_model)
# manager.update_auth_ticket_password(tg_name="Madabay", password="098173")
# manager.update_auth_ticket_password(tg_name="Mechnuna", password="123123")
# manager.update_auth_ticket_status(tg_name="Madabay", status=AuthTicketStatuses.confirmed.value)
# manager.update_auth_ticket_campus(tg_name="Madabay", campus=Campuses.Moscow.value)
# manager.update_auth_ticket_full_name(tg_name="Madabay", full_name="Ким Леонид Федорович")
# sdf = manager.select_auth_user_by_tg(tg_name="Mechnuna")
# a = manager.select_from_entry_request_by_tg("Mechnuna")
all_tik = manager.select_entry_request_status_new()
# for i in all_tik:
#     print(i)
# print(all_tik[0])

# model = (manager.select_er_universal(id_val=20))
# manager.update_er_universal(er_model=model, id_val=20, campus=Campuses.MOS.value)

manager.check_if_entry_request_creatable('Mechnuna', 'ABITUR')
print()
