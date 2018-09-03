import numpy as np
import simplekml
from coordinates import earth2rect,get_bearing
from polycircles import polycircles
from geopy.distance import lonlat, distance

class Location:
	def __init__(self, name, lng, lat):
		self.name = name
		self.lng = lng
		self.lat = lat
		self.rect = earth2rect(lng, lat)

def dist(loc1, loc2):
	loc1_pos = (loc1.lng,loc1.lat)
	loc2_pos = (loc2.lng,loc2.lat)
	# bearing = get_bearing(loc1_pos,loc2_pos)

	return distance(lonlat(*loc1_pos),lonlat(*loc2_pos)).meters


	#return np.linalg.norm(loc1.rect - loc2.rect)

class Landmark(Location):
	def __init__(self, name, lon, lat, rad, kml):
		Location.__init__(self, name, lon, lat)
		self.poly = polycircles.Polycircle(longitude=lon, latitude=lat, radius=rad, number_of_vertices=36)
		self.kml = kml.newpolygon(name=name, outerboundaryis = self.poly.to_kml())
		self.kml.style.polystyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)
