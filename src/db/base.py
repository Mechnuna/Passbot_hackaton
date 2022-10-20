"""
Подключение к БД
"""
 
from sqlalchemy import create_engine, MetaData
import os
# Формирование базовых элементов подключения к БД
# Engine базовый класс - подключение к БД (по логину / паролю) для sqlAlchemy

TEST_DB_NAME = "test.db"
dir_path = os.path.dirname(os.path.realpath(__file__))
database_url = f"sqlite+pysqlite:///{dir_path}/{TEST_DB_NAME}"

ENGINE = create_engine(database_url)
metadata = MetaData()
