from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, ForeignKeyConstraint, ForeignKey, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import sessionmaker

import config

class Conn:
	def __init__(self, mapapi_database_connector):
		self.engine = create_engine(mapapi_database_connector)
		self.m = MetaData()

	def __enter__(self):
		self.m.reflect(bind=self.engine)
		self.Base = automap_base(metadata=self.m)
		self.Base.prepare(self.engine, reflect=True)
		self.Session = sessionmaker(bind=self.engine)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.Session.close_all()

	def get_session(self):
		return self.Session()