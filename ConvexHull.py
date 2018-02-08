"""
ConvexHull.py

Author - Anthony Hernandez

This python script takes in a file name as a command line arguement in order to readin 
a set of points whose convex hull is then calculated. The resulting convex hull is written
to a file named "output.txt" that is located in the same directory as ConvexHull.py

"""
from itertools import cycle
import sys
import random

#returns a triangle from given vertices in the form of a list of vertices in clockwise order 
def Triangulate(verts):
	triangle = [verts[0]]
	#the determinant of 3 points is calculated to see if clockwise, if not, swap 2 of the points
	det = (verts[0][0]*(verts[1][1]-verts[2][1]) -verts[0][1]*(verts[1][0]-verts[2][0])
		+ (verts[1][0]*verts[2][1]-verts[2][0]*verts[1][1]))

	if det < 0: 
		triangle.append(verts[1])
		triangle.append(verts[2])
	elif det > 0:
		triangle.append(verts[2])
		triangle.append(verts[1])
	else: 	#if points are colinear, simply return the edges as a line, include all points
		return verts
	return triangle
	
	
#returns the determinant of an edge and point by creating vectors: edge[0]edge[1] and edge[0]point
#edge is a list of 2 points
#return is >0 if point rightof | <0 leftof | ==0 on line
def Side_Check(edge, point):
	tail = edge[0]
	head = edge[1]
	eVect = (head[0]-tail[0], head[1]-tail[1])
	pVect = (point[0]-tail[0], point[1]-tail[1])
	return eVect[0]*pVect[1]-eVect[1]*pVect[0]
	
#returns the upper and lower extreme edges given 2 hulls
#The hull vertices are turned into cycle lists allowing for infinite traversal until an edge is found
#using leftof and rightof checks of neighbors to vertices making an edge between the leftHull and rightHull
def Find_Extremes(leftHull, rightHull):
	found = False
	extremes = []
	leftHullC = cycle(leftHull)
	rightHullC = cycle(rightHull)
	prevL=leftHullC.next()
	curL=leftHullC.next()
	nextL=leftHullC.next()
	prevR=rightHullC.next()
	curR=rightHullC.next()
	nextR=rightHullC.next()
	while(not found):	#finds the upper extreme edge
		edge = [curL,curR]	
		if Side_Check(edge,prevL) > 0 or Side_Check(edge,nextL) > 0:
			prevL = curL
			curL = nextL
			nextL = leftHullC.next()
			continue
		if Side_Check(edge,prevR) > 0 or Side_Check(edge,nextR) > 0:
			prevR = curR
			curR = nextR
			nextR = rightHullC.next()
			continue
		else:
			found = True
			
	#upper extreme edge found, reset found for lower edge		
	extremes.append(edge)
	found = False
	
	while(not found): #finds the lower extreme edge
		edge = [curR,curL]
		if Side_Check(edge,prevL) > 0 or Side_Check(edge,nextL) > 0:
			prevL = curL
			curL = nextL
			nextL = leftHullC.next()
			continue
		if Side_Check(edge,prevR) > 0 or Side_Check(edge,nextR) > 0:
			prevR = curR
			curR = nextR
			nextR = rightHullC.next()
			continue
		else:
			found = True
	extremes.append(edge)
	return extremes	#list containing the upper extreme edge and lower extreme edge
	
#removes duplicates from a hullList to fix corner cases when combining hulls through extreme edges
def clean(hullList):
	unique = {}
	cleanList = []
	for point in hullList:
		if not point in unique:
			unique[point] = None
			cleanList.append(point)
	return cleanList

#returns merged  hulllist, conditions are included for special "wrap around cases"
def Merge(leftHull, rightHull):
	extremes = Find_Extremes(leftHull, rightHull)
	upper = extremes[0]
	lower = extremes[1]
	startTop = leftHull.index(upper[0])
	endTop = rightHull.index(upper[1])
	startBot = rightHull.index(lower[0])
	endBot = leftHull.index(lower[1])
	if startTop == endBot: #handle case where extreme edges are connected
		newHull = upper+rightHull[endTop:]+lower
	elif endTop == startBot: #handle case where extreme edges are conected
		newHull = leftHull[:startTop]+upper+lower+leftHull[endBot:]
	
	elif endTop == startBot:
		newHull = leftHull[:startTop]+upper+rightHull[endTop+1:startBot]+lower+leftHull[endBot+1:]
		
	elif endTop > startBot: #handle wrap around cases when rewriting lists 
		newHull = leftHull[:startTop]+upper+rightHull[endTop+1:]+rightHull[:startBot]+lower+leftHull[endBot+1:]
		
	elif endBot<startTop:	#handle wrap around cases when rewriting lists 
		newHull = leftHull[:startTop]+upper+rightHull[endTop+1:startBot]+lower
		
	else:
		newHull = leftHull[:startTop]+upper+rightHull[endTop+1:startBot]+lower+leftHull[endBot+1:]	
	return clean(newHull)

#divide and conquer part that splits algorithm into halves, base cases are lines or triangle, drawn clockwise
def Convex_Hull_DVQ(coords):
	n = len(coords)
	if n == 3:
		return Triangulate(coords)
	elif n == 2:
		return coords
	elif n== 1: #this should never occur
		return coords
		print("error in points")
	else:
		leftHull = Convex_Hull_DVQ(coords[:(n/2)])
		rightHull = Convex_Hull_DVQ(coords[(n/2):])
	return Merge(leftHull, rightHull)
	
#genereates a random set of points for testing purposes
def RanGen(rng, amount):
	rng = int(sys.argv[1])
	amount = int(sys.argv[2])
	print rng
	print amount

	f = open("testIn.txt", "w")
	f.write(str(amount)+"\n")
	for i in range(amount):
		f.write(str(random.randint(1,rng+1))+" "+str(random.randint(1,rng+1))+"\n") 
	f.close()

def main():
	coords = []
	f = open(sys.argv[1], "r")
	next(f)
	for line in f:
		pair = line.split(" ")
		coords.append((int(pair[0]), int(pair[1])))
	coordsU = list(set(coords))
	coordsS = sorted(coordsU, key=lambda c: [c[0], c[1]])
	hull = Convex_Hull_DVQ(coordsS)
	hullL = len(hull)
	f.close()
	f = open("output.txt", "w")
	f.write(str(hullL)+"\n")
	for pair in hull:
		f.write(str(pair[0])+" "+str(pair[1])+"\n")
	f.close()

if __name__ == '__main__':
    main()
