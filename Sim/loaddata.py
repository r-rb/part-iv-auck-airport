from plane import Plane
import numpy as np

def loadplane(apt,kml):
	plane = []
	plane.append(Plane("Rayner", 170.0, -35.0, 3, 1, apt, kml))
	plane.append(Plane("Nathan", 176.0, -39.0, 3, 2, apt, kml))
	plane.append(Plane("John", 180.0, -39.5, 0, 4, apt, kml))
	plane.append(Plane("Joe", 172.0, -36.0, 0, 5, apt, kml))
	plane.append(Plane("Anne", 173.0, -35.0, 1, 2, apt, kml))
	return plane

def loadsep(kml):
	S = np.array([	[2,2,3,4],
					[2,2,2,3],
					[0,0,0,3],
					[0,0,0,0]	])
	return S
