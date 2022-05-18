import cv2
from PIL import Image
import numpy as np

try:
	from Scripts.ManageDB.MongoDB import MongoDB, load as MongoDataLoad
except ImportError:
	import sys
	sys.path.append('../ManageDB')
	from MongoDB import MongoDB, load as MongoDataLoad

import time
mssleep = lambda x: time.sleep(x/1000)

"""
draw_objs:

Takes one picture and draws rectangle around objects in it
based on bounding boxes of object

"""

def draw_objs(im, objs):
	for classe, l in objs.items():
		for obj in l:
			coo = obj.get()
			if coo == None:
				continue
			coo = [ int(i) for i in coo ]
			im = cv2.rectangle(im, (coo[0], coo[1]), (coo[2], coo[3]), (0,255,0), 2)
			(_, _), baseline = cv2.getTextSize(classe + ' ' + str(obj.getMid()),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.75, 1)
			cv2.putText(im, classe + ' ' + str(obj.getMid()),
				(coo[0], coo[1] - baseline),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.75, (255, 255, 255), 1)
	return im

"""
scene:

Runs into video frame and count object at every frame
The result is displayed in real time on the screen
This output the parsed data of CountObject class

"""

def scene(vid_path, time_data, objs_parser):
	path = vid_path

	vid = cv2.VideoCapture(path)
	if not vid.isOpened():
		raise IOError("Couldn't open webcam or video")
	key_to_idx = list(time_data.keys())
	it_frames = 0
	while vid.isOpened():
		fdata, frame = vid.read()
		if not fdata:
			break
		try:
			objs_parser.run(key_to_idx[it_frames], time_data[key_to_idx[it_frames]])
		except IndexError:
			break
		frame = frame[:, :, ::-1]
		image = Image.fromarray(frame)
		result = np.asarray(image)
		result = draw_objs(result, objs_parser.getCurrentObjs())
		cv2.namedWindow("VIDEO", cv2.WINDOW_NORMAL)
		cv2.imshow("VIDEO", result)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		# mssleep(200)
		it_frames += 1
	vid.release()
	return objs_parser.getTime()

"""
onlyData:

Runs into video frame and count object at every frame
This output the parsed data of CountObject class

"""

def onlyData(time_data,objs_parser):
	key_to_idx = list(time_data.keys())

	for it_frames in range(len(time_data)):
		try:
			objs_parser.run(
				key_to_idx[it_frames],
				time_data[key_to_idx[it_frames]])
		except IndexError:
			break
	return objs_parser.getTime()

"""
Connexion to MongoDB with credentials "config_db"

"""

def getMongo(db_name, config_db):
	secrets = MongoDataLoad(config_db)
	mdb = MongoDB(db_name, secrets["username"],
		secrets["password"], secrets["host"])
	mdb.connect()
	return mdb

"""
Uploads count results in correct database

"""

def upMongo(link, data, loc, filename):
	link.add_to_collection(loc, [ i.get(filename) for i in data ])

if __name__ == "__main__":
	import sys
	sys.path.append('../ExportDataLocal')
	from LoadData import LoadData
	frame_time = LoadData('../../Predict/OutFrames/test01.helios').get('time_data')

	from cobject import CountObject
	co = CountObject(path_eq='../MapToPy/DataOut/test01.json')
	count_data = scene('../../Data/ExportH45/Exp11s.mp4', frame_time, co)

	from Export import ExportCSV
	ecsv = ExportCSV(count_data)
	db_format = ecsv.run()
	for obj in db_format:
		print(obj.get('fake_video_name.mp4'))
