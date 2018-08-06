import numpy as np
import math

# Radius of the earth
earth_radius = 6.371e6 # metres

# Convert geospatial earth coordinates to cartesian rectangular coordinates
def earth2rect(lon, lat):
	theta = np.deg2rad(lat)
	phi = np.deg2rad(lon)
	R = earth_radius
	x = R*np.cos(theta)*np.cos(phi)
	y = R*np.cos(theta)*np.sin(phi)
	z = R*np.sin(theta)
	return np.array([x,y,z])

# Convert rectangular coordinates back to geospatial earth coordinates
def rect2earth(coords):
	x = coords[0]
	y = coords[1]
	z = coords[2]
	R = earth_radius
	lat = np.rad2deg( math.asin(z/R) )
	lon = np.rad2deg( math.atan2(y,x) )
	return (lat, lon)

# Return weighted averages of positions at a specific time interval
def interpolate_trail(t,trail):

	max_targ = (t+1) *60 

	for idx,entry in enumerate(trail):

		if entry["ts"] <= max_targ:

			if idx == 0:
				return entry
			else:
				v1 = entry
				t1 = v1["ts"] - t *60
				v0 = trail[idx-1]
				t0 = v0["ts"] - t *60

				return {k:np.interp(0,[t0,t1],[v0[k],v1[k]]) for k in entry}