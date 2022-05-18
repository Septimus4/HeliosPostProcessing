from math import *
import numpy as np


"""
class Similarity:

compute distance calculation between two sets
of coordinates to obtain a similarity score

"""

class Similarity:
	def __init__(self) -> None:
		pass

	def euclidean_distance(self, x, y):
		return sqrt(sum(pow(a-b,2) for a, b in zip(x, y)))

	def manhattan_distance(self, x, y):
		return sum(abs(a-b) for a,b in zip(x,y))

	def get(self, x, y):
		ed = self.euclidean_distance(x, y)
		md = self.manhattan_distance(x, y)

		return np.mean([ed, md])

if __name__ == "__main__":
	r = Similarity().get([1874, 392, 1917, 491], [833, 27, 967, 249])
	print(r)