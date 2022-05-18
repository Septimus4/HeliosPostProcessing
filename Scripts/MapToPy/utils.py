import matplotlib.pyplot as plt
import json
from collections import deque

class Visu:
	@staticmethod
	def mShow(data):
		print(
			'\n'.join({ "Key: {} - Data: {}".format(key,i)\
				for key,i in data.items() })
		)

	@staticmethod
	def showMap(data):
		def _ppToPlot(data):
			x_list = []
			y_list = []
			l = []
			for k,i in data.items():
				x_list.append([ j[0] for t_i in i for j in t_i ])
				y_list.append([ j[1] for t_i in i for j in t_i ])
				l.append(k)
			return x_list,y_list,l
		x_list,y_list, key = _ppToPlot(data)
		ax = plt.subplot(1,1,1)

		for it_t_x,it_t_y,it_k in zip(x_list, y_list, key):
			print(it_k)
			ax.plot(it_t_x,it_t_y, label=it_k)
		handles, labels = ax.get_legend_handles_labels()
		ax.legend(handles, labels)
		plt.show()

class JsonWriter:
	def __init__(self,path,data):
		self.data=data
		self.path=path

	def run(self,):
		with open(self.path,'w') as t_file:
			json.dump(self.data,t_file,indent=4)

import math
def calcRatio(angle,height):
	return math.tan( math.radians(angle) )*height

def shortListByPath(tosort):
	def buildPath(l):
		return [ [ l[i],l[i+1] ]\
			for i in range(len(l)-1) ]
	def shortestPath(graph, start, end, path=[]):
			path = path + [start]
			if start == end:
				return path
			if start not in graph:
				return None
			shortest = None
			for node in graph[start]:
				if node not in path:
					newpath = shortestPath(graph, node, end, path)
					if newpath:
						if not shortest or len(newpath) < len(shortest):
							shortest = newpath
			return shortest
	res={}
	for key,i in tosort.items():
		t_res={}
		for it_i in i:
			if it_i[0] not in t_res.keys():
				t_res[it_i[0]]=[]
			if it_i[1] not in t_res.keys():
				t_res[it_i[1]]=[]
			t_res[it_i[0]].append(it_i[1])
			t_res[it_i[1]].append(it_i[0])
		for i_keys in t_res.keys():
			for j_keys in t_res.keys():
				t_path = shortestPath( t_res,i_keys,j_keys )
				if t_path!=None and len(t_path)==len(i)+1:
					res[key]=buildPath(t_path)
	return res
