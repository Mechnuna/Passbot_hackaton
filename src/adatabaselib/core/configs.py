"""
Модуль с конфигурациями:
- Конфиг подключения БД
- Параметры даты
- Некоторое описание таблиц
"""
import os
import pytz
import yaml
from enum import Enum
from typing import Optional
from pydantic import BaseModel


### DATABASE CONFIG:
class dbDialects(Enum):
    """
    Енум с наименованиями баз под которых написаны настройки
    """
    postgres = 'POSTGRES'
    sqlite = 'SQLITE'


class F_DataBaseConfig(BaseModel):
    """
    Конфиг с данными подключения к БД
    """
    DB_USERDAT: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_SERVICE: Optional[str] = None
    DB_SCHEMA: Optional[str] = None
    DATABASE_URL: Optional[str] = None  
    ADD_SCHEME: bool = False
    DB_DIALECT: str = ''

    @staticmethod
    def form_database_url(prefix: str, db_userdat = None, db_host = None, db_service=None):
        res_string = prefix + "://"
        if db_userdat:
            res_string += db_userdat + "@"
        if db_host:
            res_string += db_host
        if db_service:
            res_string += "/" + db_service
        return res_string 

   
    @classmethod
    def produce_from_yaml(cls, path: str, dialect: dbDialects, add_scheme: bool = False):
        assert dialect in dbDialects._value2member_map_
        if not isinstance(path, str):
            path = str(path)
        prefix = ''
        if os.path.isfile(path) and path.endswith(".yaml"):
            with open(path, "r") as file:
                conf: dict = yaml.full_load(file)
                DB_USERDAT = conf.get("FIAS_USERDAT")
                DB_HOST = conf.get("FIAS_HOST")
                DB_SERVICE = conf.get("FIAS_SERVICE")
                DB_SCHEMA = conf.get("FIAS_SCHEMA")

            if dialect == dbDialects.postgres.value:
                prefix = "postgresql+psycopg2"
            elif dialect == dbDialects.sqlite.value:
                prefix = "sqlite+pysqlite"
            else:
                raise AssertionError("Для данной БД не описаны настройки")          
            
            DATABASE_URL = cls.form_database_url(
                prefix=prefix,
                db_userdat=DB_USERDAT,
                db_host=DB_HOST,
                db_service=DB_SERVICE
            )
            
            return cls(
                DB_USERDAT = DB_USERDAT,
                DB_HOST = DB_HOST,
                DB_SERVICE = DB_SERVICE,
                DB_SCHEMA = DB_SCHEMA,
                DATABASE_URL = DATABASE_URL,
                ADD_SCHEME = add_scheme,
                DB_DIALECT = dialect
            )
        return cls()


class F_DataConfig:
    """
    Конфиг с правилами наименования/заполнения полей
    """
    def __init__(self, id_label: str, id_quote: bool) -> None:
        assert isinstance(id_label, str)
        assert isinstance(id_quote, bool)
        self.__id_label = id_label
        self.__id_quote = id_quote

    @property
    def id_label(self):
        return self.__id_label
    
    @property
    def id_quote(self):
        return self.__id_quote


class F_TimeConfig:
    """
    Конфиг времени
    """
    def __init__(self, timezone: str = "Europe/Moscow") -> None:
        self.__TIME_ZONE_STRING = timezone
        self.__TZ =  pytz.timezone(self.__TIME_ZONE_STRING)
        assert self.__TZ is not None
    
    @property
    def timezone(self):
        return self.__TZ     

    @property
    def timezone_name(self):
        return self.__TIME_ZONE_STRING


class F_AllConfig:
    """
    Конфиг общий
    """
    def __init__(
        self,
        dialect: dbDialects,
        db_config: F_DataBaseConfig,
        time_config: Optional[F_TimeConfig] = None,
        name: str = "default"
        ) -> None:

        assert dialect in dbDialects._value2member_map_
        self.__dialect = dialect
        
        assert isinstance(db_config, F_DataBaseConfig)
        self.__db_config = db_config
        
        if time_config is None:
            self.__time_config = F_TimeConfig()
        else:
            assert isinstance(time_config, F_TimeConfig)
            self.__time_config = time_config

        assert isinstance(name, str)
        self.__name = name

    @property
    def dialect(self) -> dbDialects:
        return self.__dialect

    @property
    def db_config(self) -> F_DataBaseConfig:
        return self.__db_config

    @property
    def tz_config(self) -> F_TimeConfig:
        return self.__time_config
    
    @property
    def name(self) -> str:
        return self.__name
