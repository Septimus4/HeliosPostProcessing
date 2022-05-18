#!/usr/bin/env python3
##
## RODOLPHE COLLEIE, 2020
## Helios
## File description:
## Take video as an input, split it and send it to the db
##

import sys

sys.path.insert(1, '../ManageDB')
from MongoDB import MongoDB as mydb
from MongoDB import load

import os
import argparse
import re
import math
from subprocess import check_call, PIPE, Popen
import shlex

duration = re.compile('Duration: (\d{2}):(\d{2}):(\d{2}(\.\d+)?)')
fps = re.compile('(\d+(\.\d+)?) fps')

def arg_parser():
	parser = argparse.ArgumentParser(description="Split given video and send it to MongoDB")
	parser.add_argument("json", help="Load the file's content to connect to the database")
	parser.add_argument("video", help="The video to split and send to the database")
	if parser.parse_args() is None:
		sys.exit(1)

# Retrieves info from the given video thanks to ffmpeg
def get_metadata(filename):
	p1 = Popen(["ffmpeg", "-hide_banner", "-i", filename], stdout=PIPE, stderr=PIPE, universal_newlines=True)
	output = p1.communicate()[1]
	return output

# Get the video's fps and length in seconds
def extract_metadata(output):
	dur = duration.search(output)
	fps_count = fps.search(output)
	if dur and fps_count:
		video_length = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3))
		video_fps = float(fps_count.group(1))
	else:
		raise Exception("Can't parse required metadata")
	return video_length, video_fps

# Split the given video in segments of n seconds
def split_segment(filename, n, by='size'):
	assert n > 0
	assert by in ['size', 'count']
	split_size = n if by == 'size' else None
	split_count = n if by == 'count' else None

	output = get_metadata(filename)
	video_length, video_fps = extract_metadata(output)

	split_count = math.ceil(video_length / split_size)
	split_size = round(video_length / split_count)
	pth, ext = filename.rsplit(".", 1)
	cmd = 'ffmpeg -hide_banner -loglevel panic -i "{}" -c copy -map 0 -segment_time {} -reset_timestamps 1 -g {} -sc_threshold 0 -force_key_frames "expr:gte(t,n_forced*{})" -f segment -y "{}%d.{}"'.format(filename, split_size, round(split_size*video_fps), split_size, pth, ext)
	check_call(shlex.split(cmd), universal_newlines=True)
	# return list of output (index start from 0)
	return ['{}{}.{}'.format(pth, i, ext) for i in range(split_count)]

# Send the parts to the database then removes the local files
def split_and_send(db, filename, location):
	parts = split_segment(filename, 20, by='size')
	for part in parts:
		_id = db.upload_video(part, location)
		if _id is None:
			return
		os.remove(part)

if __name__ == "__main__":
	args = arg_parser()
	data = load(sys.argv[1])
	db = mydb(data["name"], data["username"], data["password"], data["host"])
	db.connect()
	split_and_send(db, sys.argv[2], "Toulouse-Compans")
	db.disconnect()
