from pathlib import Path
import os

try:
	from Scripts.ExportDataLocal.ReadExpFrames import ReadExpFrame
except ImportError:
	from ReadExpFrames import ReadExpFrame

"""
class LoadData:

Load all data from saved protobuf structure
The data is sorted by time and by id

Usage:

ld = LoadData(path_to_export)
ld.get(x)

"""

class LoadData:
	def __init__(self, path, *args, **kwargs) -> None:
		path = "{0}_{2}{1}".format(*os.path.splitext(path) + (str(0),))
		self.path = Path(path)
		if not self.path.exists():
			raise FileNotFoundError
		self.load()

	def load(self):
		ref = ReadExpFrame(self.path)
		ref.run()
		self.time_data = ref.get('bytime')
		self.frameid_data = ref.get('byframeid')
		self.location = ref.getLocation()

	def get(self, toget):
		if not hasattr(self, toget):
			return None
		return self.__getattribute__(toget)

	def getForCount(self):
		return self.time_data, self.location

if __name__ == "__main__":
	ld = LoadData('./Data/yl_demo.helios')
	tdata = ld.get('time_data')
	print(tdata)
