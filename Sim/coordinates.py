import numpy as np
import math
import geopy

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

# Takes in tuples of (long,lat) returns bearing to B from A.
def calculate_initial_compass_bearing(pointA, pointB):

    lat1 = math.radians(pointA[1])
    lat2 = math.radians(pointB[1])

    diffLong = math.radians(pointB[0] - pointA[0])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing