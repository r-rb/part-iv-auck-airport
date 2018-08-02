###################################################

### MODULES

###################################################

import numpy as np
import json
import simplekml
from collections import defaultdict
from polycircles import polycircles

###################################################

### PARAMETERS

###################################################

fields = {"To", "From"} # These are the fields in the JSON file which we check for the phrase "Auckland".
auck_names = {"Auckland", "auckland"} # These are the phrases we search for in the JSON file to show that a plane is leaving or bound for Auckland Airport.

json_min = 0
json_max = 800 # The number of minutes worth of JSON files we process, in this range

dec_horiz_rad = 1e20 # metres, Decision horizon radius

###################################################

### CONSTANTS

###################################################

# The coordinates of Auckland Airport
auck_air_lat = -37.013383 # degrees
auck_air_long = 174.779962	# degrees

# The radius around the airport to enclose the runway
auck_air_rad = 4000 # metres

# Radius of the earth
earth_radius = 6.371e6 # metres

###################################################

### FUNCTIONS

###################################################

# Convert geospatial earth coordinates to cartesian rectangular coordinates
def earth2rect(lat, longit):
	theta = np.deg2rad(lat)
	phi = np.deg2rad(longit)
	R = earth_radius
	x = R*np.cos(theta)*np.cos(phi)
	y = R*np.cos(theta)*np.sin(phi)
	z = R*np.sin(theta)
	return np.array([x,y,z])

###################################################

### EVALUATE RECTANGULAR COORIDINATE OF AIRPORT

###################################################

auck_air_rect = earth2rect(auck_air_lat,auck_air_long)

###################################################

### GO THROUGH JSON FILES

###################################################

# These are the things we will record
timestamp = defaultdict(list)
longit = defaultdict(list)
lat = defaultdict(list)
auck_air_dist = defaultdict(list)
in_airport = defaultdict(list)


for k in range(json_min,json_max+1):
	print(k)
	if k/100.0 - int(k/100.0) < 0.595:
		with open('2018-04-06-'+str(k).zfill(4)+'Z.json') as json_data: # For each minute,
			try:
				d = json.load(json_data) # d stands for data
				for ac in d["acList"]: # ac stands for aircraft
					if "Lat" in ac.keys() and "Long" in ac.keys(): # Provided we have latitude and longitude to record,
						record_ac = False
						rect = earth2rect(ac["Lat"],ac["Long"])
						dist = np.linalg.norm(rect-auck_air_rect)
						icao = ac["Icao"]

						if ac["Icao"] in timestamp.keys():
							record_ac = True
						else:
							for field in fields: # inspect each field
								if field in ac.keys(): # (some aircraft do not have all fields)
									for name in auck_names: # Check if the plane is bound for Auckland
										if name in ac[field]:
											record_ac = True

							if dist <= 2*auck_air_rad:
								record_ac = True

						if record_ac and dist <= dec_horiz_rad and (not timestamp[icao] or timestamp[icao][-1] != k):
							timestamp[icao].append(k)
							longit[icao].append(ac["Long"])
							lat[icao].append(ac["Lat"])
							auck_air_dist[icao].append(dist)
							in_airport[icao].append(dist <= auck_air_rad)
			except:
				print("Skipped...")

for icao in timestamp.keys():
	print(str(len(timestamp[icao])))

###################################################

### RECORD TO KML

###################################################

# Create the file
kml=simplekml.Kml()

depart_times = defaultdict(list)
arrive_times = defaultdict(list)

for icao in timestamp.keys():
	ls = kml.newlinestring(name=icao)

	T = len(timestamp[icao])
	for t in range(T):
		ls.coords.addcoordinates([(longit[icao][t],lat[icao][t])])
		if t>0 and in_airport[icao][t] != in_airport[icao][t-1]:
			if in_airport[icao][t-1]:
				depart_times[icao].append(timestamp[icao][t])
			else:
				arrive_times[icao].append(timestamp[icao][t])

print(arrive_times)
print(depart_times)

auck_air_circle = polycircles.Polycircle(latitude=auck_air_lat,
                                    longitude=auck_air_long,
                                    radius=auck_air_rad,
                                    number_of_vertices=36)
auck_air = kml.newpolygon(name="Auckland Airport", outerboundaryis=auck_air_circle.to_kml())
auck_air.style.polystyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)
kml.save('fooline.kml');
