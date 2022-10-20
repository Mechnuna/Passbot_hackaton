## Описание БД

### ENTRYREQUEST
- id (pk) - NUMBER - "уникальный ID записи"
- tg_contact - VARCHAR - "Телеграм ник создавщего запрос"
- name_initiator (ФИО) - VARCHAR - "ФИО создавшего запрос"
- nick_responsible (fk) - VARCHAR - "Ник ответственного в слаке"
- name_responsible - VARCHAR - "Имя отвественного"
- name_guest (fk) - VARCHAR - "Имя гостя"
- guest_type - VARCHAR - "Тип гостя"
- booking_date - DATE - "День брони на пропуск"
- creation_date - DATE - "Дата создания записи"
- update_date - DATE - "Дата обновления записи"
- ticket_status - VARCHAR - "Статус тикета"

### inviting_inner_users
- nick_responsible (pk) - VARCHAR - "Ник отвественного в слаке"
- tg_contact - "Телеграм-ник ответственного"
- name_responsible - VARCHAR - "Имя отвественного"
- role (fk) - VARCHAR - "Тип роли ответственного"
- current_invited - NUMBER - "Кол-во активных приглашений"
- block_operations - BOOLEAN - "Блок юзера"

### guests
- name_guest - VARCHAR - "Имя гостя" (pk)
- currently_invited - BOOLEAN - "Приглашение активно"
- block_operations - BOOLEAN - "Блок гостя"

### roles
- role (pk) - VARCHAR - "Тип роли"
- max_for_invite - NUMBER - "Максимальное кол-во для инвайта"
