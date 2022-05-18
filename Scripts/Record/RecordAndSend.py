#!/usr/bin/env python3
##
## RODOLPHE COLLEIE, 2020
## Helios
## File description:
## Recording videos from picamera and send them to mongo
##

import sys

sys.path.insert(1, '../ManageDB')
from MongoDB import MongoDB as mydb
from MongoDB import arg_parser
from MongoDB import load

import os
import io
import random
import picamera
from signal import signal, SIGINT

part = 0

'''
Writes the recorded video locally
'''

def write_video(stream, location):
	global part
	part = part + 1
	name = location + str(part) + ".mp4"
	print('Saving video {}'.format(name))
	with stream.lock:
		for frame in stream.frames:
			if frame.frame_type == picamera.PiVideoFrameType.sps_header:
				stream.seek(frame.position)
				break
		with io.open(name, 'wb') as output:
			output.write(stream.read())
		return name

'''
Records continually in a 10s circular buffer with the picamera module
Send each part to the mongodb database
'''

def record(db, location):
	camera = picamera.PiCamera()
	stream = picamera.PiCameraCircularIO(camera, seconds=10)
	camera.rotation = 180
	camera.start_recording(stream, format='h264')
	try:
		while True:
			camera.wait_recording(5)
			name = write_video(stream, location)
			_id = db.upload_video(name, location)
			if _id is None:
				return
			os.remove(name)
	finally:
		camera.stop_preview()
		camera.stop_recording()

if __name__ == "__main__":
	args = arg_parser()
	data = load(sys.argv[1])
	db = mydb(data["name"], data["username"], data["password"], data["host"])
	db.connect()
	record(db, "Saint-Jean-de-Luz")
	db.disconnect()
