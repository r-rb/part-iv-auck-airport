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
	lng = np.rad2deg( math.atan2(y,x) )
	return (lng, lat)

