import pprint as pp
import pandas as pd

lines = open("april_9.txt","r").readlines()

scheduled_times = [x.split('\t')[0] for x in lines[0::4]]
plane_models= [x.split('\t')[1].split(' ')[0] for x in lines[2::4]]

lines = open('aircraft_code.txt','r').readlines()

iata = [x.split('\t')[0] for x in lines]
icao = [x.split('\t')[1] for x in lines]
classes = [x.split('\t')[-1] for x in lines]

wake_class = []

for model in plane_models:

    try:
        wake_class.append(classes[iata.index(model)])
    except  (IndexError, ValueError) as e:
        try:
            wake_class.append(classes[icao.index(model)])
        except  (IndexError, ValueError) as e:
            wake_class.append('M')
    

pp.pprint(len(plane_models))
pp.pprint(len(wake_class))