import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sql_username = os.environ.get('SQL_USERNAME')
sql_password = os.environ.get('SQL_PASSWORD')
sql_host = os.environ.get('SQL_HOST')
sql_port = os.environ.get('SQL_PORT')
sql_database = os.environ.get('SQL_DATABASE')

sql_engine = create_engine(
    f'postgresql+psycopg2://{sql_username}:{sql_password}@{sql_host}:{sql_port}/{sql_database}'
)
sql_session = sessionmaker(bind=sql_engine)
