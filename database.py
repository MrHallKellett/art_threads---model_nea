import sqlite3
from config import *

class Database:

	def  __enter__(self):
		self.__connection = sqlite3.connect(DB_FILENAME)
		self.__cursor = self.__connection.cursor()
		return self

	def __exit__(self, type, value, traceback):
		self.__connection.close()

	def execute(self, query, values=None, one_row=False):
		if values:
			results = self.__cursor.execute(query, values)
		else:
			results = self.__cursor.execute(query)
		self.__connection.commit()
		if one_row:
			return results.fetchone()
		else:
			return results.fetchall()
		

