try:
	from Scripts.CountObject.Similarity import Similarity
	from Scripts.DetectStreetObject.FindLocation import find_street
except ImportError:
	from Similarity import Similarity
	import sys
	sys.path.append('../DetectStreetObject')
	from FindLocation import find_street

"""
class ObjSaver:

Create new object in order to count objects in video
The location corresponds to the street where is the object
The location is updated if it changes
Every coordinates of the object in stored
We are able to track the object from the moment when it enters
in the video to the moment when it lefts the video

Usage:

objs = ObjSaver(id_of_object,
	coordinates_of_current_location)

"""

class ObjSaver:
	def __init__(self, mid, coo, *args, **kwargs) -> None:
		self.mid = mid
		self.coo = [ coo ]
		self.last_coo = coo
		self.locations = []

		self.threshold = 0
		self.freeze = False

	def add(self, new_coo):
		self.threshold = 0
		self.coo.append(new_coo)
		self.last_coo = new_coo

	def updateLocation(self, location):
		if not location in self.locations and location != None:
			self.locations.append(location)

	def get(self):
		self.threshold += 1
		if self.threshold > 25 or self.freeze:
			self.freeze = True
			return None
		return self.last_coo

	def getMid(self):
		return self.__getattribute__('mid')

	def getLocation(self):
		return self.locations

"""
class CountObject:

This class counts object in video depending on their position in the frame
The object is considered as the same if its coefficient of similarity
(depending on last coordinates) is behind 700
For multiple objects, the smaller coefficient is taken
For every object, the location is updated at each frame

The list of objects is sorted by type of object (car, people, ...)
and time (split every hours)

The script running into video frame needs to call the method run(...)
at each frame

Usage:

co = CountObject()
for frame in ...
	obj_in_frame = ...
	current_time = ...
	co.run(current_time, obj_in_frame)
counted_objs = co.getTime()

"""

class CountObject:
	def __init__(self, *args, **kwargs) -> None:
		self.objs = {}
		self.compute_sim = Similarity()

		self.classes = [
			'pedestrian',
			'people',
			'bicycle',
			'car',
			'van',
			'truck',
			'tricycle',
			'awningtricycle',
			'bus',
			'motor' ]
		self.tab_time = {}
		self.map_equiv = kwargs.get('path_eq')

	def similarity(self, current, tocheck):
		if not tocheck:
			return 1000
		return self.compute_sim.get(current, tocheck)

	def check(self, obj, coo):
		if not obj in self.objs:
			self.objs[obj] = [ ObjSaver(it, i) for it, i in enumerate(coo) ]
		else:
			for it_coo in coo:
				sim = [ (i, self.similarity(it_coo, i.get()))\
					for i in self.objs[obj] ]
				max_sim = min(sim, key=lambda x: x[1])
				if max_sim[1] < 700:
					max_sim[0].add(it_coo)
				else:
					self.objs[obj].append(ObjSaver(len(self.objs[obj]), it_coo))

		for it_obj in self.objs[obj]:
			it_obj.updateLocation(find_street(
				it_obj.get(),
				self.map_equiv))

	def run(self, current_time, current_frame):
		hour = current_time.split(':')[1]

		if hour not in self.tab_time:
			self.objs = {}
			self.tab_time[hour] = self.objs
		else:
			self.tab_time[hour] = self.objs
		for mclass in self.classes:
			if mclass in current_frame and len(current_frame[mclass]) > 0:
				self.check(mclass, current_frame[mclass])

	def getCurrentObjs(self):
		return self.objs

	def getTime(self):
		return self.tab_time

if __name__ == "__main__":
	sys.path.append('../ExportDataLocal')
	from LoadData import LoadData
	frame_time = LoadData('../../Predict/OutFrames/test01.helios').get('time_data')

	co = CountObject(path_eq='../MapToPy/DataOut/test01.json')

	for time, coo in frame_time.items():
		co.run(time, coo)
	print(co.getTime())