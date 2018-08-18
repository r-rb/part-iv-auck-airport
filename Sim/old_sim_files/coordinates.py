import numpy as np
import math
import geopy

def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def airport_eta(lat,lng,distance,speed = False):
	aa_lat,aa_lng = -37.004833314,174.78833018 

	new_lat,new_lng = None,None

	bearing = calculate_initial_compass_bearing((aa_lat,aa_lng),(lat,lng))

	origin = geopy.Point(lat, lng)

	destination = geopy.VincentyDistance(meters=distance).destination(origin, bearing

	destination.
	if speed:
		new_eta = get_new_eta(new_lat,new_lng,speed)

	return {"new_lat": new_lat,
				"new_lng": new_lng,
					"new_eta": None if not speed else new_eta}


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