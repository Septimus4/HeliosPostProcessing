import unittest

from ExpFrame import ExpFrame
from ExpFrame import HandleLabelMapTf
from ExpFrame import ParseFrameTf

from ReadExpFrames import ReadExpFrame

from testdata import test_data

import os

import numpy as np

class TestExpFrame(unittest.TestCase):
	def test_load_notexists(self,):
		with self.assertRaises(FileNotFoundError):
			ef = ExpFrame('./notexists.helios','location','tf')
			ef.load()

	def test_bad_keys(self,):
		ef = ExpFrame('./ut.helios','location1','tf')
		with self.assertRaises(TypeError):
			ef.run( ['invalid','data'],'14:22' )

	def test_bad_values(self,):
		ef = ExpFrame('./ut.helios','location1','tf')
		with self.assertRaises(TypeError):
			ef.run( { 'num_detections':None,'detection_boxes':None,
				'detection_scores':None,'detection_classes':None },'14:22' )

	def test_bad_nbobjs(self,):
		ef = ExpFrame('./ut.helios','location1','tf')
		with self.assertRaises(ValueError):
			ef.run( { 'num_detections':-50,'detection_boxes':None,
				'detection_scores':None,'detection_classes':None },'14:22' )

	def test_export(self,):
		ef=ExpFrame('./ExpUnittest/test_export_ut.helios','location1','tf')
		ef.run(dict(test_data),'14:22')
		self.assertIsNot(os.path.exists('./ExpUnittest/test_export_ut_0.helios'),False)

	def test_path(self,):
		ef=ExpFrame('./ExpUnittest/test_export_ut.helios','location1','tf')
		ef.run(dict(test_data),'14:22')
		self.assertIsNot(os.path.exists('./ExpUnittest/test_export_ut_0.helios'),False)
		ef=ExpFrame('./ExpUnittest/TestPath/test_export_ut.helios','location1','tf')
		ef.run(dict(test_data),'14:22')
		self.assertIsNot(os.path.exists('./ExpUnittest/test_export_ut_0.helios'),False)

	#Export modulo10 pour les saves
	def test_save(self,):
		ef=ExpFrame('./ExpUnittest/test_export_ut.helios','location1','tf')
		for i in range(11):
			ef.run(dict(test_data),'14:2'+str(i))
		self.assertIsNot(os.path.exists('./ExpUnittest/test_export_ut_0_save.helios'),False)

class TestHandleLabelMapTf(unittest.TestCase):
	def __init__(self,*args,**kwargs):
		super(TestHandleLabelMapTf, self).__init__(*args, **kwargs)

		self.c_hlm = HandleLabelMapTf('./TestModel/Data/labelmap.pbtxt')

	def test_loadlmap(self,):
		with self.assertRaises(FileNotFoundError):
			HandleLabelMapTf('./notfound.pbtxt')

	def test_getInvalidLabel(self,):
		with self.assertRaises(IndexError):
			self.c_hlm.getByLabel('IncorrectLabel')
			self.c_hlm.getByLabel(42)
			self.c_hlm.getByLabel(['list','is','incorrect'])
			self.c_hlm.getByLabel({'dict':'is','also':'incorrect'})

	def test_getInvalidValue(self,):
		with self.assertRaises(ValueError):
			self.c_hlm.getByValue('IncorrectValue')
			self.c_hlm.getByValue(42)
			self.c_hlm.getByValue(['list','is','incorrect'])
			self.c_hlm.getByValue({'dict':'is','also':'incorrect'})

	def test_validValueAndRtValue(self,):
		t_lmap_idx = [ self.c_hlm.getByValue(i) for i in range(1,4) ]
		[ self.assertEqual( type(t_value),str ) for t_value in t_lmap_idx ]

	def test_validLabelAndRtLabel(self,):
		t_lmap_values = [ self.c_hlm.getByLabel(i) for i in [ 'car','people','bike' ] ]
		[ self.assertEqual( type(t_value),int ) for t_value in t_lmap_values ]

class TestParseFrameTf(unittest.TestCase):
	def test_bad_type(self,):
		with self.assertRaises(TypeError):
			ParseFrameTf( ['invalid','data'],'14:22','1' )

	def test_bad_keys(self,):
		with self.assertRaises(KeyError):
			ParseFrameTf( {'invalid':'data'},'14:22','1' )

	def test_incorrectframeid(self,):
		with self.assertRaises(TypeError):
			ParseFrameTf( ['invalid','data'],'14:22',1 )

	def test_bad_values(self,):
		with self.assertRaises(TypeError):
			ParseFrameTf( { 'num_detections':None,'detection_boxes':None,
				'detection_scores':None,'detection_classes':None },'14:22','1' )

	def test_bad_nbobjs(self,):
		with self.assertRaises(ValueError):
			ParseFrameTf( { 'num_detections':-50,'detection_boxes':None,
				'detection_scores':None,'detection_classes':None },'14:22','1' )

	def test_checkdata(self,):
		t_test_data = { **dict(test_data) , **{'keytest':'Bonjour'} }
		pf=ParseFrameTf( t_test_data,'14:22','1' )
		t_col = ['detection_boxes','detection_scores','detection_classes','keytest']
		t_res = pf.checkData( col=t_col )
		self.assertIs(t_res,True)

	def test_reformat(self,):
		pf=ParseFrameTf(dict(test_data),'14:22','1')
		self.assertIs( type(pf.__getattribute__('f_data')),dict )

	def test_validaddObj(self,):
		from predhelios.protoc_pb2 import PredObject
		pf=ParseFrameTf(dict(test_data),'14:22','1')
		t_obj = pf.addObj( np.array([32,32]),np.float32(10.2) )
		self.assertIs(type(t_obj),PredObject)

	def test_invalidcoo(self,):
		pf=ParseFrameTf(dict(test_data),'14:22','1')
		with self.assertRaises(TypeError):
			t_obj = pf.addObj( 'Bonjour',np.float32(10.2) )

	def test_invalidscore(self,):
		pf=ParseFrameTf(dict(test_data),'14:22','1')
		with self.assertRaises(TypeError):
			t_obj = pf.addObj( np.array([32,32]),'Bonjour' )

	def test_recFillStruct(self,):
		from predhelios.protoc_pb2 import Frame
		c_hlm = HandleLabelMapTf('./TestModel/Data/labelmap.pbtxt')
		pf = ParseFrameTf( dict(test_data),'14:22','1' )
		t_frame = pf.recFillStruct(c_hlm)
		self.assertIs(type(t_frame),Frame)

class TestReadExpFrame(unittest.TestCase):
	def test_invalidpath(self,):
		with self.assertRaises(FileNotFoundError):
			ReadExpFrame('invalidpath')

	def test_goodpath(self,):
		rf = ReadExpFrame('./Data')
		self.assertIs(type(rf),ReadExpFrame)
		rf = ReadExpFrame('./Data/test_followup_0.helios')
		self.assertIs(type(rf),ReadExpFrame)

	def test_goodpathinvaliddata(self,):
		with self.assertRaises(ValueError):
			rf = ReadExpFrame('./testdata.py')
		with self.assertRaises(FileNotFoundError):
			rf = ReadExpFrame('./TestModel')

if __name__ == "__main__":
	unittest.main()