#!/usr/bin/env python3
##
## RODOLPHE COLLEIE, 2020
## Helios
## File description:
## Find location of a given object
##

import math
import argparse
import sys
import json
from jsonschema import validate
from PIL import Image, ImageDraw
from random import randint

try:
	from Scripts.DetectStreetObject.utils import getDistance
except ImportError:
	from utils import getDistance

"""
This module permits to find the nearest vector (xy,xy) of a point (x,y)
The point is the position of the predicted object (by our model) and the vectors are the roads on the video
The map of vectors is contained is .json file which stores the roads following the format:

"Name of the street":[
	[
		[x0,y0],[x1,y1]
	],
	[
		[x2,y2],[x3,y3]
	]
]

The street can be cut in several parts.
Each pairs of coordinates corresponds to start and end of segment of the street.

Usage:

find_street((x_min, y_min, x_max, y_max), json_file_with_vectors.json)

"""

def arg_parser():
	parser = argparse.ArgumentParser(description="Find location of a given object")
	parser.add_argument("file", help="Use the file's content to connect to obtain a list of streets")
	parser.add_argument("x", help="Abscissa of the object you want to locate")
	parser.add_argument("y", help="Ordinate of the object you want to locate")

	return parser.parse_args()

def load(filename):
	schema = {
		"type" : "object"
	}
	try:
		f = open(filename)
		data = json.load(f)
		validate(instance=data,schema=schema)
		f.close()
	except Exception as e:
		print("Invalid .json %s" % e)
		sys.exit(1)
	return data

def check_errors():
	arg_parser()

	try:
		x = float(sys.argv[2])
		y = float(sys.argv[3])
		data = load(sys.argv[1])
	except ValueError as e:
		print("Invalid number: %s" % e)
		sys.exit(1)
	return x, y, data

output = []
def remove_nestings(l):
	for i in l:
		if type(i) == list:
			remove_nestings(i)
		else:
			output.append(i)

def list_streets(data):
	streets = []

	for name, segment in data.items():
		street = []
		street_name = str(name)
		remove_nestings(segment)
		parts = output.copy()
		street.append(street_name)
		street.append(parts)
		streets.append(street)
		output.clear()
	return streets

def calc_line_coef(A, B):
	a = B[0] - A[0]
	b = B[1] - A[1]
	c = a * A[0] + b * A[1]
	return a, b, -c

def calc_dist(point, line):
	coef = calc_line_coef(line[0], line[1])
	a = coef[0]
	b = coef[1]
	c = coef[2]

	if (a == 0 and b == 0):
		return math.sqrt((line[0][0] - point[0]) ** 2 + (line[0][1] - point[1]) ** 2)
	return abs(a * point[0] + b * point[1] + c) / math.sqrt(a ** 2 + b ** 2)

def find_closest_dist(point, lines_list):
	l = len(lines_list)
	closest_dist = sys.maxsize

	for i in range(0, l, 4):
		line = ((lines_list[i], lines_list[i + 1]),
				(lines_list[i + 2], lines_list[i + 3]))
		dist, _ = getDistance(point, line)
		if (dist < closest_dist):
			closest_dist = dist
	return closest_dist

def find_street(point, streets, exp_streets=False):
	if point == None:
		return None
	street_name = ""
	closest_dist = sys.maxsize
	data = load(streets)
	streets = list_streets(data)

	point = [ point[0],point[3] ]

	for street in streets:
		name = street[0]
		dist = find_closest_dist(point, street[1])
		if (dist < closest_dist):
			closest_dist = dist
			street_name = name
	if exp_streets:
		return street_name, streets
	return street_name

if __name__ == "__main__":
	a = arg_parser()
	OBJ = (int(a.x), 0, 0, int(a.y))
	n_street, st = find_street(OBJ, a.file, exp_streets=True)
	print('Nearest vector:', n_street)

	image = Image.open('./f1.png')
	img = ImageDraw.Draw(image)
	colors = ['blue', 'red', 'green', 'white', 'gray']
	it = 0
	for _,i in st:
		img.line(i, fill=colors[it], width = 350)
		it+=1

	for _,i in st:
		_, near = getDistance(
			(int(a.x), int(a.y)),
			[(i[0],i[1]), (i[2],i[3])])
		print(_, near)
		img.line([(int(a.x), int(a.y)), near],fill =colors[it],width = 4)
		it+=1
	image.show()