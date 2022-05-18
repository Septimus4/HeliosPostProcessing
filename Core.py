import json
from jsonschema import validate

import os
from pathlib import Path

from Scripts.ExportDataLocal.ExpFrame import ExpFrame
from Predict.Predict_main import Predictor, model
from Scripts.CountObject.CountAndExport import getMongo, scene, onlyData, upMongo
from Scripts.CountObject.Export import ExportCSV
from Scripts.ExportDataLocal.LoadData import LoadData
from Scripts.ModelSender.GetAndSend import MongoGFS, GetLastVideo, getCredentials
from Scripts.CountObject.cobject import CountObject

def loadConfig(path = './Config/config.json'):
	if not Path(path).exists():
		raise Exception(
			'Error: "./Config/config.json" not found')
	f = open(path)
	data = json.load(f)
	checkConfig(data)
	f.close()
	return data

def checkConfig(data):
	schema = {
		"type": "object",
		"properties":{
			"is_demo": {"type": "boolean"},
			"location": {"type": "string"},
			"config_mongo": {"type": "string"},
			"db_get": {"type": "string"},
			"db_upload": {"type": "string"},
			"config_mongo": {"type": "string"},
			"expframe_config": {"type": "object", "properties": {
				"filepath": {"type": "string"},
				"method": {"type": "array"}
			}},
			"expy_pred": {"type": "string"},
			"model_config": {"type": "object", "properties":{
				"model_path": {"type": "string"},
				"anchors_path": {"type": "string"},
				"classes_path": {"type": "string"},
				"score": {"type": "number", "minimum":0.0, "maximum":1.0},
				"model_image_size": {"type": "array"}
			}},
			"path_eq": {"type": "string"},
		},
	}
	try:
		validate(data, schema=schema)
	except Exception as e:
			raise Exception(e)

"""
class Core:

Main pipeline for IA Prediction
It triggers when a new video is uploaded in MongoDB, and follow the following pipeline:
- The video is downloaded
- The video is sent to the model which outputs predictions
- The predictions are saved formatted in a protobuf structure
- The predictions are loaded by the counting module, which will
analyse each frames of the video to count objects
- The counting result is exported in database format
- The result is uploaded to MongoDB database

The program never quits, except Ctrl+C

The Core takes a path to a configuration file in .json
The config file contains every data needed for this pipeline

Example of config file:

{
	"location":"test01",
	"config_mongo":"./Config/mongodb.json",
	"db_get":"VideoToModel",
	"db_upload":"IAAnalysis",
	"expframe_config": {
		"filepath":"./Predict/OutFrames/test01.helios",
		"method":["yolo", "./Config/FilesToPred/new_classes_order.txt"]
	},
	"expy_pred":"./Predict/OutFrames/test01.helios",
	"model_config": {
		"model_path": "./LastModel_yv3/yolov3_15102020_final.h5",
		"anchors_path": "./Config/FilesToPred/yolo_anchors.txt",
		"classes_path": "./Config/FilesToPred/data_classes.txt",
		"score": 0.5,
		"model_image_size": [416, 416]
	},
	"path_eq":"./Scripts/MapToPy/DataOut/test01.json"
}

Usage:

config = loadConfig()
Core(config).heliosia()

"""

class Core:
	def __init__(self, config, *args, **kwargs) -> None:
		self.config = config
		self.mgfs = MongoGFS(
			self.config['db_get'],
			getCredentials(
				self.config['config_mongo']))
		self.dwl = GetLastVideo()
		self.model = model(self.config['model_config'])

	def interupt(self):
		self.model.close_session()

	def heliosia(self, show_graphics=False):
		for f in self.mgfs.getWCursor(self.config['location']):
			temp_video_path = self.dwl.get(self.mgfs, f)
			if self.config['is_demo'] == False:
				exp_y_pred = ExpFrame(
					filepath=self.config['expframe_config']['filepath'],
					method=self.config['expframe_config']['method'],
					location=self.config['location'])
				print("Running model on video...")
				Predictor(self.model, temp_video_path).run(
					expy_pred=exp_y_pred,
					show_video=show_graphics)
			print("Loading model predictions...")
			time_data, loc = LoadData(
				self.config['expframe_config']['filepath']).getForCount()
			print("Counting model predictions...")
			if show_graphics:
				exp_time = scene(temp_video_path, time_data, CountObject(
					path_eq=self.config['path_eq']))
			else:
				exp_time = onlyData(time_data, CountObject(
					path_eq=self.config['path_eq']))
			print("Exporting model predictions...")
			format_data = ExportCSV(exp_time).run()
			print("Upload to MongoDB...")
			if len(format_data) == 0:
				print("Done...")
				continue
			link_db = getMongo(
				self.config['db_upload'],
				self.config['config_mongo'])
			upMongo(link_db, format_data, loc, os.path.basename(temp_video_path))
			link_db.disconnect()
			print("Done...")
		self.model.close_session()

if __name__ == "__main__":
	config = loadConfig()
	c = Core(config)
	try:
		c.heliosia()
	except KeyboardInterrupt:
		c.interupt()
	except (FileNotFoundError, ValueError, IndexError):
		print('Error: Invalid path in config file...')
		c.interupt()