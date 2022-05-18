try:
	from Scripts.ExportDataLocal.predhelios import protoc_pb2
except ImportError:
	from predhelios import protoc_pb2

import numpy as np

import os
import warnings

"""
Disable warning starting warnings of tensorflow

"""
warnings.simplefilter(
	action='ignore',
	category=(FutureWarning,DeprecationWarning)
)
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

"""
class ParseFrameXX:

Format frame prediction and fill it in protobuf structure
It stores bouding boxes, accuracy and the type of object

There are two similar classes : ParseFrameTf & ParseFrameYl
One is for tensorflow prediction format and the other is for yolo v3 prediction format

Usage:
pyl = ParseFrameYl(prediction_data, real_time_of_frame, id_of_frame)
ProtobufObject = pyl.run(label_map_handle)

"""

class ParseFrameTf:
	def __init__(self, data, time, frame_id):
		self.tofill = protoc_pb2.Frame()
		self.tofill.time = time
		self.tofill.frame_id = frame_id
		if type(data) != dict:
			print('Error: Incorrect type of data')
			raise TypeError
		self.data = data
		if not self.checkData():
			print('Error: Incorrect frame detection')
			raise KeyError
		self.nobjs = self.data.pop('num_detections')
		if self.nobjs<0:
			print('Error: Invalid number of objects')
			raise ValueError
		self.tofill.n_objs = self.nobjs
		self.reFormat()

	def reFormat(self):
		self.f_data={ key:i[:self.nobjs] for key,i in self.data.items() }

	def checkData(self, col=['num_detections','detection_boxes',\
		'detection_scores','detection_classes']):
		t_data = dict(self.data)
		return False if not set(col).issubset(t_data) else True

	@staticmethod
	def addObj(coo, score):
		toadd = protoc_pb2.PredObject()
		if type(coo) != np.ndarray:
			print('Error: Incorrect coordinate format')
			raise TypeError
		toadd.coo.extend(coo)
		if type(score)!=np.float32:
			print('Error: Incorrect score format')
			raise TypeError
		toadd.score = score
		return toadd

	def recFillStruct(self, lmaputils, itobj=0):
		if itobj==self.nobjs:
			return self.tofill
		self.tofill.__getattribute__(
			lmaputils.getByValue(self.f_data['detection_classes'][itobj])
		).append(self.addObj(
			self.f_data['detection_boxes'][itobj],
			self.f_data['detection_scores'][itobj]
		))
		return self.recFillStruct(lmaputils, itobj+1)

	def run(self, lmaputils):
		return self.recFillStruct(lmaputils)

class ParseFrameYl:
	def __init__(self,data,time,frame_id):
		self.tofill = protoc_pb2.Frame()
		self.tofill.time = time
		self.tofill.frame_id = frame_id
		if type(data) != list:
			print('Error: Incorrect type of data')
			raise TypeError
		self.data = data
		if not self.checkData():
			print('Error: Incorrect frame detection')
			raise KeyError
		self.nobjs = len(self.data)
		self.tofill.n_objs = self.nobjs

	def checkData(self):
		for i in self.data:
			if len(i) != 6:
				return False
		return True

	def addObj(self,coo,score):
		toadd = protoc_pb2.PredObject()
		if type(coo) != list:
			print('Error: Incorrect coordinate format')
			raise TypeError
		toadd.coo.extend(coo)
		if type(score)!=np.float32:
			print('Error: Incorrect score format')
			raise TypeError
		toadd.score = score
		return toadd

	def recFillStruct(self,lmaputils,itobj=0):
		if itobj==self.nobjs:
			return self.tofill
		self.tofill.__getattribute__(
			lmaputils.getByValue(self.data[itobj][4])
		).append(self.addObj(
			[ self.data[itobj][i] for i in range(4) ],
			self.data[itobj][5]
		))
		return self.recFillStruct( lmaputils,itobj+1 )

	def run(self,lmaputils):
		if self.nobjs<=0:
			return self.tofill
		return self.recFillStruct(lmaputils)

"""
class HandleLabelMapXX:

Loads label map to be able to convert id to label in label name and invert
The label map is generaly a file file labels associated with ids

There are two similar classes : HandleLabelMapTf & HandleLabelMapYl
One is for tensorflow label map format and the other is for yolo v3 label map format
The tensorflow label map is formated as follow:

item {
  id: 1
  name: 'x'
}

item {
  id: 2
  name: 'x'
}

The yolo label map is formated as follow:

x
x
x

Usage:

hlmyl = HandleLabelMapYl(path_to_labelmap)
corresponding_id = hlmyl.getByLabel('x')
corresponding_label = hltyl.getByValue(1)

"""

class HandleLabelMapTf:
	def __init__(self, path):
		if not os.path.exists(path):
			print('Error: Label map not found')
			raise FileNotFoundError
		# self.labelmap = label_map_util.\
		# 	get_label_map_dict(path)

	def getByLabel(self,label):
		if not label in self.labelmap.keys():
			print('Error: Incorrect label')
			raise IndexError
		return self.labelmap[label]

	def getByValue(self,value):
		if not value in self.labelmap.values():
			print('Error: Incorrect value')
			raise ValueError
		return list(self.labelmap.keys())[
			list(self.labelmap.values()).index(value)]

class HandleLabelMapYl:
	def __init__(self,path):
		if not os.path.exists(path):
			print('Error: Label map not found')
			raise FileNotFoundError
		t_file = open(path)
		self.labelmap = { i.split('\n')[0]:it\
			for it,i in enumerate(t_file.readlines()) }
		t_file.close()

	def getByLabel(self,label):
		if not label in self.labelmap.keys():
			print('Error: Incorrect label')
			raise IndexError
		return self.labelmap[label]

	def getByValue(self,value):
		if not value in self.labelmap.values():
			print('Error: Incorrect value')
			raise ValueError
		return list(self.labelmap.keys())[
			list(self.labelmap.values()).index(value)]

"""
class OpFiles:

Creates path of output files which will contains filed protobuf structure
and creates new path is the size of the current file is above 500Mo

Usage:

if not OpFiles().size(base_path_of_file):
	self.fpath = self.m_opfiles.buildpath(
		base_path_of_file, id_of_current_file)

"""

class OpFiles:
	def __init__(self):
		self.lsize = (1e+9)/2 #500MO
		#self.lsize = 10000

	def rename(self,old,f_id):
		if not os.path.exists(old):
			print('Error renaming',old,' : File not found')
			raise FileNotFoundError
		new = self.buildpath( old,f_id )
		os.rename(old,new)
		return new

	def buildpath(self,filename,m_id):
		return "{0}_{2}{1}".format(*os.path.splitext(filename) + (m_id,))

	def size(self,path):
		if not os.path.exists(path):
			print('Error: File not found')
			raise FileNotFoundError
		return True if os.path.getsize(path)<=self.lsize else False


"""
class ExpFrame:

Main class to convert prediction data into protobuf formart
and save the protobuf structure into a file
This class iterates into all predictions of a video
and fills at each iteration the structure

You can take a look of the protobuf structure in the file : "predhelios.protoc"
The structure contains a location to define where the video has been recorded
Then, there is a list of frames with frame id, number of object detected in the frame,
and the informations on the objects

At the end of the input data, this class exports all the
serialized protobuf structure in a file

Usage:

random_test_data = ...
ef = ExpFrame(
	'path_to_export_file.helios',
	'location_of_the_video',
	['yolo', path_to_label_map])
for i in range(1000):
	ef.run(random_test_data, time)

"""

class ExpFrame:
	def __init__(self, filepath, location, method):
		self.tofill = protoc_pb2.Data()
		self.tofill.location = location
		self.fileid = 0
		self.b_fpath = filepath
		self.m_opfiles = OpFiles()
		self.fpath =\
			self.m_opfiles.buildpath(filepath,self.fileid)
		self.frame_id = 0
		self.save_fpath = self.m_opfiles.buildpath(self.fpath,'save')
		self.loadMethod(method)

	def loadMethod(self, method):
		equivpmethod = {
			#'tf':(ParseFrameTf,HandleLabelMapTf('./TestModel/Data/labelmap.pbtxt')),
			'yolo':(ParseFrameYl,HandleLabelMapYl(method[1])) }
		if not method[0] in equivpmethod.keys():
			print('Error: Incorrect method of parsing')
			raise KeyError
		self.parser,self.oplmap = equivpmethod[method[0]]

	def load(self,):
		if not os.path.exists(self.fpath):
			print('Error: File not found')
			raise FileNotFoundError
		t_file = open(self.fpath, "rb")
		self.tofill.ParseFromString(t_file.read())
		t_file.close()

	def export(self,fpath=False):
		t_file = open(self.fpath if not fpath else fpath,'wb')
		t_file.write(self.tofill.SerializeToString())
		t_file.close()

	def getnFrameId(self):
		if (self.frame_id != 0) and ((self.frame_id%10)==0):
			if not OpFiles().size(self.fpath):
				self.fileid+=1
				self.fpath =\
					self.m_opfiles.buildpath(self.b_fpath,self.fileid)
				self.save_fpath =\
					self.m_opfiles.buildpath(self.fpath,'save')
				self.tofill = protoc_pb2.Data()
			self.export(self.save_fpath)
		t_frameid = self.frame_id
		self.frame_id+=1
		return t_frameid

	def run(self,framedata,time):
		self.tofill.data.append(
			self.parser(framedata,time,self.getnFrameId()).run(self.oplmap)
		)
		self.export()
		return self.tofill

if __name__ == "__main__":
	from Data.testyldata import yldatatest
	ef = ExpFrame('./Data/yl_demo.helios','Location',[
		'yolo',
		'../../Config/FilesToPred/new_classes.txt'])
	for i in range(10):
		ef.run(yldatatest,'Time'+str(i))
