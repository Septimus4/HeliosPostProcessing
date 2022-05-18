import os
import pymongo
import gridfs

import json

"""
class MongoGFS:

Initialize connexion with Mongo Grid FS to upload and download large files
This classes allow connexion following credentials containing in "cred"
and to the database "db_name"

The method getWCursor(...) returns a trigger connected to the database :
The trigger acts as an iterable variable
When a new file is uploaded containing in this field the location
corresponding to "loc" parameter, the trigger is activated and the new
element can be directly used in real time by our program
The trigger has queue capabilities, so the new files are all accesible while iterating
the trigger even if an element is uploaded while program is working

If a "fileid" (Mongo identifiant) is passed through get(...) method,
it will get the full content of the file identified by "fileid"

Usage:

mgfs = MongoGFS(name_of_database, json_credentials_of_db)
for new_file in mgfs.getWCursor(temporary_loc):
	file_id = ...(new_file)
	file_data = mgfs.get(file_id)
	...

"""

class MongoGFS:
	def __init__(self, db_name, cred, *args, **kwargs) -> None:
		self.load(db_name, cred)
		self.finfo_collection = kwargs.get(
			'finfo', 'fs.files')

	def getWCursor(self, loc):
		return self.db[self.finfo_collection].watch(
			[{'$match': {'fullDocument.location': loc}}])

	def getFileList(self, it):
		self.files = { it['fullDocument']['_id']:it['fullDocument'] }
		return self.files

	def load(self, db_name, cred):
		url = 'mongodb+srv://'\
			+cred['username']\
			+':'\
			+cred['password']\
			+'@'\
			+cred['host']\
			+'/'+db_name\
			+'?retryWrites=true&w=majority'
		self.connector = pymongo.MongoClient(url)
		self.db = self.connector[db_name]
		self.fs = gridfs.GridFS(self.db, collection='fs')

	def get(self, mid=None):
		if type(mid) != str:
			if mid not in self.files:
				return None
			return self.fs.get(mid).read()
		if not hasattr(self, mid):
			return None
		return self.__getattribute__(mid)

"""
class GetLastVideo:

Gets last video uploaded on the database and downloads it
The videos are sorted by uploadDate
The path is defined by filename in the database

Usage:

glv = GetLastVideo()
path = glv.get(pointer_to_MongoGFS_class, file)

"""

class GetLastVideo:
	def getLastFile(self):
		last_upload = max(
			self.files.values(),
			key=lambda x: x['uploadDate'])
		return last_upload

	def get(self, pt_mgfs, f):
		self.files = pt_mgfs.getFileList(f)
		if len(self.files) == 0:
			return None
		last = self.getLastFile()
		w_path = os.path.join('./dwl/', last['filename'])
		print('Downloading...')
		file = pt_mgfs.get(last['_id'])
		print('Writing...')
		self.writer(w_path, file)
		print('Done...')
		return w_path

	@staticmethod
	def writer(file, data, method='bytes'):
		f = open(file, {
			'bytes':'wb',
			'string':'w'}[method])
		f.write(data)
		f.close()

def getCredentials(path):
	f = open(path)
	data = json.load(f)
	f.close()
	return data

def wrapGetAndSend(db_name, config_mongo, location=''):
	cred = getCredentials(config_mongo)
	return GetLastVideo(db_name, cred).get(location)

if __name__ == "__main__":
	mgfs = MongoGFS('VideoToModel', getCredentials('../../Config/mongodb.json'))
	for new_file in mgfs.getWCursor('test_loc'):
		video_path = GetLastVideo().get(mgfs, new_file)
		print(video_path)
