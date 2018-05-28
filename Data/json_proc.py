import json
from collections import defaultdict
import matplotlib.pyplot as plt
import simplekml

def search(myDict, lookup):
    for key, value in myDict.items():
        for v in value:
            if lookup in v:
                return key

fields = {"To", "From"}
json_max = 17;

longit = defaultdict(list)
lat = defaultdict(list)

for k in range(0,json_max+1):
	with open('2018-04-06-'+str(k).zfill(4)+'Z.json') as json_data:
		d = json.load(json_data)
		for ac in d["acList"]:
			for field in fields:
				if field in ac.keys():
					if "Auckland" in ac[field]:
						if "Lat" in ac.keys() and "Long" in ac.keys():
							longit[ac["Icao"]].append(ac["Long"])
							lat[ac["Icao"]].append(ac["Lat"])

#plt.scatter(lat['7C7AAC'],longit['7C7AAC'])
#plt.show()

kml=simplekml.Kml()

for icao in lat.keys():
	ls = kml.newlinestring(name=icao)

	N = len(lat[icao])
	for i in range(N):
		ls.coords.addcoordinates([(longit[icao][i],lat[icao][i])])

kml.save('fooline.kml');
