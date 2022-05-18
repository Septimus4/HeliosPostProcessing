try:
	from Scripts.ExportDataLocal.predhelios import protoc_pb2
except ImportError:
	from predhelios import protoc_pb2
import os

def findInDir(pathdir,ext):
	return [ os.path.join(root, file)\
		for root, dirs, files in os.walk(pathdir)\
			for file in files\
				if file.endswith(ext) and not file.startswith('save_') ]

"""
class ReadExpFrame:

Parses the protobuf structure and transforms the informations
in exploitable data
Only predictions with accuracy above "bscore" are kept to have more confident data

It generates two lists :
One of the data sorted by time
One of the data sorted by frame id

There are several possibilities to get the data :
get(x) : Returns variable identified by name "x" contained in the class if it exists
getById(x) : Returns data of the frame "x"
getByTime(x) : Returns data at time "x"
getObjectByTime(x) : Returns all data corresponding at "x" object in data sorted by time
getObjectById(x) : Returns all data corresponding at "x" object in data sorted by frame id
getObjectInId(x, y) : Returns data of object "y" at frame id "x"
getObjectInTime(x, y) : Returns data of object "y" at time "x"

Usage:

ref = ReadExpFrame(path_to_protobuf_export)
ref.run()
result = ref.getById(id_to_find)

"""

class ReadExpFrame:
	def __init__(self, fpath, bscore=0.3):
		if not os.path.exists(fpath):
			print('Error: File not found')
			raise FileNotFoundError
		self.fpath = fpath
		self.data = protoc_pb2.Data()
		self.error=False
		if os.path.isdir(fpath):
			self.dload(self.fpath)
		else:
			self.load()
		if self.error==True:
			raise ValueError
		self.basescore = bscore
		self.location = self.data.location

	def reformat(self,):
		self.bytime = {}
		self.byframeid = {}
		for frame in self.data.data:
			self.bytime[frame.time] = {
				'pedestrian':[i.coo for i in frame.pedestrian if i.score>self.basescore],
				'people':[i.coo for i in frame.people if i.score>self.basescore],
				'bicycle':[i.coo for i in frame.bicycle if i.score>self.basescore],
				'car':[i.coo for i in frame.car if i.score>self.basescore],
				'van':[i.coo for i in frame.van if i.score>self.basescore],
				'truck':[i.coo for i in frame.truck if i.score>self.basescore],
				'tricycle':[i.coo for i in frame.tricycle if i.score>self.basescore],
				'awningtricycle':[i.coo for i in frame.awningtricycle if i.score>self.basescore],
				'bus':[i.coo for i in frame.bus if i.score>self.basescore],
				'motor':[i.coo for i in frame.motor if i.score>self.basescore] }
			self.byframeid[frame.frame_id] = {
				'pedestrian':[i.coo for i in frame.pedestrian if i.score>self.basescore],
				'people':[i.coo for i in frame.people if i.score>self.basescore],
				'bicycle':[i.coo for i in frame.bicycle if i.score>self.basescore],
				'car':[i.coo for i in frame.car if i.score>self.basescore],
				'van':[i.coo for i in frame.van if i.score>self.basescore],
				'truck':[i.coo for i in frame.truck if i.score>self.basescore],
				'tricycle':[i.coo for i in frame.tricycle if i.score>self.basescore],
				'awningtricycle':[i.coo for i in frame.awningtricycle if i.score>self.basescore],
				'bus':[i.coo for i in frame.bus if i.score>self.basescore],
				'motor':[i.coo for i in frame.motor if i.score>self.basescore] }

	def get(self, toget=None):
		if hasattr(self, toget):
			return self.__getattribute__(toget)
		return None

	def getError(self, m_id, data):
		if m_id not in data:
			return False
		return True

	def getById(self,idtofind):
		if not self.getError( idtofind,self.byframeid.keys() ):
			raise IndexError
		return self.byframeid[idtofind]

	def getByTime(self,timetofind):
		if not self.getError( timetofind,self.bytime.keys() ):
			raise IndexError
		return self.bytime[timetofind]

	def getObjectByTime(self,idobject):
		if not self.getError( idobject,
			list(self.bytime.values())[0].keys() ):
			raise IndexError
		return { key:i[idobject]\
			for key,i in self.bytime.items() }

	def getObjectById(self,idobject):
		if not self.getError( idobject,
			list(self.byframeid.values())[0].keys() ):
			raise IndexError
		return { key:i[idobject]\
			for key,i in self.byframeid.items() }

	def getObjectInId(self,idtofind,idobject):
		return self.getById(idtofind)[idobject]

	def getObjectInTime(self,timetofind,idtofind):
		return self.getByTime(timetofind)[idtofind]

	def dload(self,files):
		l_files = sorted(findInDir(files,'.helios'))
		if len(l_files)<=0:
			print('Error: ".helios" files not found in input directory')
			raise FileNotFoundError
		for pfile in l_files:
			t_file = open(pfile,'rb')
			try:
				self.data.ParseFromString(t_file.read())
			except Exception as e:
				print(e)
				self.error=True
			t_file.close()

	def load(self,):
		t_file = open(self.fpath, "rb")
		try:
			self.data.ParseFromString(t_file.read())
		except Exception as e:
			print(e)
			self.error = True
		t_file.close()

	def run(self,):
		self.reformat()

	def getLocation(self):
		return self.location

if __name__ == "__main__":
	t = ReadExpFrame('./Data/yl_demo_0.helios')
	t.run()
	test = t.getObjectInId(2, 'bicycle')
	print(test)