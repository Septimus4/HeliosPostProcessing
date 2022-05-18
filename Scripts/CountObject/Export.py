from datetime import date

"""
class ExportObj:

Transforms object in database format
The object is caracterized by the following properties :
its hour, its location and its number of elements for each class
(cars, peoples, ...)

To get the database format representation you must call the method get(...)
This method takes in parameter the filename of the video linked to theses
results as all the outputs are stored in the same database, we need to
deferenciate them

Database format:
{
	StartHour: int,
	StreetName: str,
	CurrentTime: int,
	ListObjs: Object,
	AssociatedVideo: str
}

To add list of objects you must call the method fullUpdate(...) with
python dict formatted as follow:
{'car': 2, 'bus': 10, ...}

Usage:

eo = ExportObj(hour, name_of_street)
eo.fullUpdate(list_of_object)
eo.get(example_filename)

"""

class ExportObj:
	def __init__(self, hour, location, *args, **kwargs) -> None:
		self.hour = hour
		self.location = location
		self.up_time = str(date.today())
		self.l = {}

	def fullUpdate(self, data):
		self.l = dict(data)

	def __repr__(self) -> str:
		return str(self.hour)\
			+ ' '\
			+ str(self.location)\
			+ ' ' + str(self.l)

	def get(self, filename):
		return {
			'StartHour':self.hour,
			'StreetName':self.location,
			'CurrentTime':self.up_time,
			'ListObjs':self.l,
			'AssociatedVideo': filename }

"""
class ExportCSV:

Parse and format data to match the database format
It will iterates into the counted data and makes objects ready to be
stored in the database
The input data must be an output of CountObject class

Usage:

ecsv = ExportCSV(count_data)
db_format = ecsv.run()

"""

class ExportCSV:
	def __init__(self, data, *args, **kwargs) -> None:
		self.data = data
		self.export = {}
		self.attrib = []

	def reformat(self):
		self.export = {}
		self.l = []
		for hour, classe in self.data.items():
			if hour not in self.export:
				self.export[hour] = {}
			for it_classe, l_objs in classe.items():
				for obj in l_objs:
					t_street = obj.getLocation()
					for it_street in t_street:
						if it_street not in self.export[hour]:
							self.export[hour][it_street] = {}
						if it_classe not in self.export[hour][it_street]:
							self.export[hour][it_street][it_classe] = 0
						self.export[hour][it_street][it_classe] += 1

		for hour, streets in self.export.items():
			for it_streets, classes in streets.items():
				ex_obj = ExportObj(hour, it_streets)
				ex_obj.fullUpdate(classes)
				self.l.append(ex_obj)

	def run(self):
		self.reformat()
		return self.l

if __name__ == "__main__":
	import sys
	sys.path.append('../ExportDataLocal')
	from LoadData import LoadData
	frame_time = LoadData('../../Predict/OutFrames/test01.helios').get('time_data')

	from cobject import CountObject
	co = CountObject(path_eq='../MapToPy/DataOut/test01.json')

	for time, coo in frame_time.items():
		co.run(time, coo)
	count_data = co.getTime()
	ecsv = ExportCSV(count_data)
	db_format = ecsv.run()
	for obj in db_format:
		print(obj.get('fake_video_name.mp4'))
