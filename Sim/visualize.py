import os
import simplekml
from subprocess import DEVNULL, STDOUT, check_call

def visualize(kml_name):
	with open(os.devnull, 'wb') as devnull:
		check_call(['gnome-maps', kml_name], stdout=DEVNULL, stderr=STDOUT)
