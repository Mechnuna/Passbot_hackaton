from operator import and_
from sqlalchemy.engine import Engine
from sqlalchemy import Table, select, text, update, and_
from typing import Optional

#  Модуль с базовыми классами для транзакций БД, остальные crud-классы наследуются от них
class BaseCRUD:
    """
    Базовый класс для работы с подключениями к БД.
    Работает транзакционно с автокоммитом.
    Включает в себя:
        - объект класса sqlalchemy.Engine для подключений
        - реализацию базовых процедур по исполнению sql-скриптов
    """
 
    def __init__(self, engine: Engine, schema = None):
        self.engine = engine
        self.schema = schema

    def __cursor_options(self, cursor, option: Optional[str] = None, n: int = 0):
        """
        Исполнение операций по извлечению данных из курсора. 
        Реализовано внутри connection cursor в одну транзакцию, а не через возврат cursor объекта с последующим извлечением.
        
        Неправильно: return ( cursor := engine.execute() ) -> (закрытие транзакции) -> cursor.fetchone()
        В этом случае:
        - После закрытия транзации могут возникать ошибки при фетче данных (так как курсор будет закрыт),
        - Работает медленнее

        """
        result = None
        if option is not None:
            try:
                if option == "fetchone":
                    result = cursor.fetchone()
                elif option == "fetchall":
                    result = cursor.fetchall()
                elif option == "fetchmany":
                    result = cursor.fetchmany(n)
                elif option == "scalar":
                    result = cursor.scalar()
                else:
                    pass
            except Exception:
                pass
        return result
    
    # Исполнение скрипта / базовый метод:
    def execute(self, query, arguments=None, option: Optional[str] = None, n: int = 0):
        """
        Подключение к БД и исполнение sql-скрипта (объект, не текст)
        На вход принимает:
            - query - скрипт для исполнения (не строка, а объект query)
            - argument - dict - используется для строковых подстановок
        Возвращает объект типа sqlalchemy.engine.CursorResult
       
        Конструкция контекста with включает в себя начало сессии и коммит
        по умолчанию
        """
        # Разделение необходимо для предотвращения ошибок
        options_kwargs= {"autocommit": True}
        result = None
        if arguments is None:
            with self.engine.connect() as connection:
                cursor = connection.execution_options(**options_kwargs).execute(query)
                result = self.__cursor_options(cursor=cursor, option=option, n=n)
        else:
            with self.engine.connect() as connection:
                cursor = connection.execution_options(**options_kwargs).execute(query, arguments)
                result = self.__cursor_options(cursor=cursor, option=option, n=n)
        return result
   
    def execute_like_stream(self, query, arguments=None, amount: int = 100):
        """
        Подключение к БД и исполнение sql-скрипта (объект, не текст)
        На вход принимает:
            - query - скрипт для исполнения (не строка, а объект query)
            - argument - dict - используется для строковых подстановок
        Возвращает объект типа sqlalchemy.engine.CursorResult
       
        Конструкция контекста with включает в себя начало сессии и коммит
        по умолчанию
        """
        # Разделение необходимо для предотвращения ошибок
        options_kwargs= {"autocommit": True, "stream_results": True}
        assert amount > 0
        
        if arguments is None:
            with self.engine.connect() as connection:
                cursor = connection.execution_options(**options_kwargs).execute(query)
                for partial_res in cursor.yield_per(amount):
                    yield partial_res
        else:
            with self.engine.connect() as connection:
                cursor = connection.execution_options(**options_kwargs).execute(query, arguments)
                for partial_res in cursor.yield_per(amount):
                    yield partial_res


    # Получение всех результатов:
    def fetchall(self, query, arguments=None):
        return self.execute(query, arguments, "fetchall")
   
    # Получение N-строк результата:
    def fetchmany(self, query, n, arguments=None):
        return self.execute(query, arguments, "fetchmany", n)
   
    # Получение результата (одна строка):
    def fetchone(self, query, arguments=None):
        return self.execute(query, arguments, "fetchone")
 
    # Получение численного результата:
    def execute_scalar(self, query, arguments=None):
        return self.execute(query, arguments, "scalar")

    @staticmethod
    def query_basic_select(select_clause, select_from_clause=None, where_clause = None, order_by_clause = None):
        if select_clause is None:
            return None
        query = select(select_clause)
        if select_from_clause is not None:
            query = query.select_from(select_from_clause)
        if where_clause is not None:
            query = query.where(where_clause)
        if order_by_clause is not None:
            query = query.order_by(order_by_clause)
        return query

    @staticmethod
    def query_basic_update(table_to_update, where_clause, values_clause: dict):
        query = update(table_to_update)
        if where_clause is not None:
            query = query.where(where_clause)
        if values_clause is not None:
            query = query.values(**values_clause)
        return query

    @classmethod
    def query_basic_select_for_update(cls, table_to_select, where_clause, of_column: str, nowait: bool = True):
        query = cls.query_basic_select(
            select_clause=table_to_select,
            where_clause=where_clause
        ).with_for_update(nowait=nowait, of=table_to_select.c[of_column])
        return query

    def decorator_connection_session(function):
        """
        Декоратор. Для исполнения скриптов внутри функции через сессию.
        Выполнение скриптов типа .execute() должно быть реализовано через аргумент connection
        (он должен быть в прототипе функции)
        """
        def wrapper(self, *args, **kwargs):
            result = None
            with self.engine.begin() as connection:
                result = function(self, *args, **kwargs, connection=connection)
            return result
        return wrapper


class TableCRUD(BaseCRUD):
    """
    Базовый класс работы с таблицами, наследуется от BaseCRUD
    Включает в себя:
        - объект класса sqlalchemy.Engine для подключений
        - поле для имени таблицы
        - реализацию базовых процедур по исполнению sql-скриптов
    """
    def __init__(self, engine: Engine, table: Table, schema=None):
        super().__init__(engine, schema)
        self.table = table
        self.table_name = table.name

    def query_truncate(self):
        """
        Более быстрый вариант очистки таблицы, чем стандартный delete
        """
        return text(f"TRUNCATE TABLE {self.table}")
    
    def query_get_all(self):
        query = self.table.select()
        return query
    
    def get_all(self):
        return self.fetchall(query=self.query_get_all())

    def query_select_this_table_for_update(
        self,
        of_column: str,
        where_clause):
        query = self.query_basic_select_for_update(
            table_to_select=self.table,
            where_clause=where_clause,
            of_column=of_column)
        return query
    
    def create_where_clause(self, param_list: list):
        """
        list[dict]
        {
            column: x,
            argument: y
        }
        """
        where_list = []
        where_clause = None
        for d in param_list:
            if d.get("argument") is not None:
                where_list.append(d.get("column") == d.get("argument"))
        if where_list:
            where_clause = and_(*where_list)
        return where_clause
    
    
    @staticmethod
    def filter_none_values(dict_to_filter: dict):
        if dict:
            res_dict = {k:v for k,v in dict_to_filter.items() if v is not None}
            return res_dict
        else:
            return None

    def query_update_this_table_by_model(self, dict_model, where_clause):
        pre_dict = dict_model.dict()
        val_dict = self.filter_none_values(dict_to_filter=pre_dict)
        query = self.table.update().values(**val_dict).where(where_clause)
        return query
    