from sqlalchemy import Table
from sqlalchemy.dialects import (
	oracle as sa_oracle,
	postgresql as sa_postgres,
	sqlite as sa_sqlite
)
from adatabaselib.core.configs import dbDialects

def insert_into_base_string(table: Table, dialect = dbDialects.sqlite.value, custom_columns: list = None):
	"""
	Создает строку под инсерт c байндами для будущих вставок аргументов (для cx_Oracle под executemany) 
	"""
	sa_dialect = None
	if dialect == dbDialects.oracle.value:
		sa_dialect = sa_oracle.dialect()
	elif dialect == dbDialects.postgres.value:
		sa_dialect = sa_postgres.dialect()
	elif dialect == dbDialects.sqlite.value:
		sa_dialect = sa_sqlite.dialect()
	else:
		return None
	
	if (custom_columns is not None) and isinstance(custom_columns, list):
		return str(table.insert().values(**dict.fromkeys(custom_columns, None)).compile(dialect=sa_dialect))
	
	return str(table.insert().values([None for _ in table.columns]).compile(dialect=sa_dialect))
