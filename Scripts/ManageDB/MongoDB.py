#!/usr/bin/env python3
##
## RODOLPHE COLLEIE, 2020
## Helios
## File description:
## Remotely connecting to MongoDB
##

import argparse
import sys
import json
from jsonschema import validate
import pymongo
from pymongo import MongoClient
import pprint
from pprint import pprint
import datetime
import gridfs

class MongoDB:
	def __init__(self, database_name, user, password, host="localhost"):
		self.host = host
		self.db_name = database_name
		self.usr = user
		self.passwd = password
		self.client = None
		self.connected = False
		self.collections = None

	def __append_data(self,):
		return ("mongodb+srv://" + self.usr + ":" +
				self.passwd + "@" + self.host + "/" +
				self.db_name + "?retryWrites=true&w=majority")

	def display_status(self,):
		if self.connected == True:
			print("Successfully connected to the database " + self.db_name)
		else:
			print("Successfully disconnected from the database " + self.db_name)

	def connect(self,):
		connec_data = self.__append_data()
		try:
			self.client = pymongo.MongoClient(connec_data)
			self.db = self.client[self.db_name]
			self.fs = gridfs.GridFS(self.db)
			self.connected = True
		except Exception as e:
			print("Error while connecting to MongoDB : ", e)
			self.client = None
			self.db = None
			self.fs = None
			self.connected = False
			sys.exit(1)
		self.__get_collection_names()
		self.display_status()

	def __get_collection_names(self,):
		filter = {"name": {"$regex": r"^(?!system\.)"}}
		self.collections = self.db.list_collection_names(filter=filter)

	def list_collection_names(self,):
		print("The present collections are:")
		print(*self.db.list_collection_names(), sep=", ")

	def display_collection_content(self, collection):
		cursor = self.db[collection].find({})
		for doc in cursor:
			print(doc)

	# Create the collection if non existent, appends the document otherwise
	def add_to_collection(self, col_name, content):
		self.db[col_name].insert_many(content)

	'''
	Add a video to the database with its name and location
	content = Bytes converted vido
	n = video's part number
	location = Where the video was recorded
	'''
	def add_video(self, content, n, location):
		try:
			_id = self.fs.put(content, filename=str(n), location=location)
			print("Successfully upload video {} to the database".format(n))
		except Exception as e:
			print("An error occurred while uploading {} to the database: {}".format(n, e))
			return None
		return _id

	def upload_video(self, filename, location):
		f = open(filename, "rb")
		v = f.read()
		f.close()
		name = filename.rsplit('/', 1)[-1]
		name = name.split('.', 1)[0]
		return self.add_video(v, name, location)

	# Retrieves a video's data from the data
	def get_video(self, name, location):
		data = None
		name = str(name)

		for grid_data in self.fs.find({"filename": name, "location": location}):
	 		data = grid_data.read()
		if data == None:
			print('No data found for the filters filename= ', name, 'and location=', location)
		return data

	# List stored videos on the db
	def list_video(self):
		print(self.fs.list())

	def delete_collection(self, col_name):
		self.db[col_name].drop()

	def delete_all(self,):
		for collection in self.collections:
			self.delete_collection(collection)

	def disconnect(self,):
		if self.connected == True :
			self.client.close()
			self.connected = False
			self.display_status()

def load(filename):
	schema = {
		"type" : "object",
		"oneOf": [{"required": ["name", "username", "password"]}],
		"properties" : {
			"host" : {"type" : "string"},
			"name" : {"type" : "string"},
			"username" : {"type" : "string"},
			"password" : {"type" : "string"},
			}
    }
	try:
		data = json.load(open(filename))
		validate(instance=data, schema=schema)
	except Exception as e:
		print("Invalid .json: %s" % e)
		sys.exit(1)
	return data

def arg_parser():
	parser = argparse.ArgumentParser(description="Manages our MongoDB")
	parser.add_argument("file", help="Use the file's content to connect to the database")
	if parser.parse_args() is None:
		sys.exit(1)
