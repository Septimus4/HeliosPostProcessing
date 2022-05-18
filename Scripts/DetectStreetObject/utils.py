import math

"""
Set of mathematicals operations used to find to closest vector to a point

"""

def dot(v,w):
	x,y = v
	X,Y = w
	return x*X + y*Y

def length(v):
	x,y = v
	return math.sqrt(x*x + y*y)

def vector(b,e):
	x,y = b
	X,Y = e
	return (X-x, Y-y)

def unit(v):
	x,y = v
	mag = length(v)
	return (x/mag, y/mag)

def distance(p0,p1):
	return length(vector(p0,p1))

def scale(v,sc):
	x,y = v
	return (x * sc, y * sc)

def add(v,w):
	x,y = v
	X,Y = w
	return (x+X, y+Y)

"""
Function that takes in parameters X,Y coordinates of a point, (x0,y0),(x1,y1) coordinates of a vector
Return the distance between the point and the vector
and the nearest point in the vector related to the object point

Ex: For point (20,600) and vector (645,0),(645,225) it outputs:
728.8689868556626 (645.0, 225.0)

"""

def getDistance(pnt, line):
	start, end = line
	line_vec = vector(start, end)
	pnt_vec = vector(start, pnt)
	line_len = length(line_vec)
	line_unitvec = unit(line_vec)
	pnt_vec_scaled = scale(pnt_vec, 1.0/line_len)
	t = dot(line_unitvec, pnt_vec_scaled)
	if t < 0.0:
		t = 0.0
	elif t > 1.0:
		t = 1.0
	nearest = scale(line_vec, t)
	dist = distance(nearest, pnt_vec)
	nearest = add(nearest, start)
	return dist, nearest