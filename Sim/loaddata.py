from plane import Plane
from location import Landmark
import numpy as np

def loadplane(kml):
	# Aiports
	akl = Landmark("Auckland Airport", 174.779962, -37.013383, 4000, kml)
	wlg = Landmark("Wellington Airport", 174.807598, -41.3275941, 4000, kml)

	plane = []
	#plane.append(Plane("Rayner", 170.0, -35.0, 3, 1, apt, kml))
	#plane.append(Plane("Nathan", 176.0, -39.0, 3, 2, apt, kml))
	#plane.append(Plane("John", 180.0, -39.5, 0, 4, apt, kml))
	#plane.append(Plane("Joe", 172.0, -36.0, 0, 5, apt, kml))
	#plane.append(Plane("Anne", 173.0, -35.0, 1, 2, apt, kml))
	plane.append(Plane("AKL-WLG1", 174.80759839999996, -41.3275941, 3, 2, [akl,wlg,akl,wlg], kml))
	return plane

def loadsep(kml):
	S = np.array([	[2,2,3,4],
					[2,2,2,3],
					[0,0,0,3],
					[0,0,0,0]	])
	return S
