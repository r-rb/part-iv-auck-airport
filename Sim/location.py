import numpy as np
import simplekml
from coordinates import earth2rect
from polycircles import polycircles

class Location:
	def __init__(self, name, lng, lat):
		self.name = name
		self.lng = lng
		self.lat = lat
		self.rect = earth2rect(lng, lat)

def dist(loc1, loc2):
	return np.linalg.norm(loc1.rect - loc2.rect)

class Landmark(Location):
	def __init__(self, name, lon, lat, rad, kml):
		Location.__init__(self, name, lon, lat)
		self.poly = polycircles.Polycircle(longitude=lon, latitude=lat, radius=rad, number_of_vertices=36)
		self.kml = kml.newpolygon(name=name, outerboundaryis = self.poly.to_kml())
		self.kml.style.polystyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)
