import os
import simplekml
from subprocess import DEVNULL, STDOUT, check_call

kml_name = "sim.kml"

def visualize(kml):
	kml.save(kml_name)

	with open(os.devnull, 'wb') as devnull:
		check_call(['gnome-maps', kml_name], stdout=DEVNULL, stderr=STDOUT)
