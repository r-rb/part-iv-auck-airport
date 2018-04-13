import pprint as pp
import pandas as pd

lines = open("april_9.txt","r").readlines()

scheduled_times = [x.split('\t')[0] for x in lines[0::4]]
plane_models= [x.split('\t')[1].split(' ')[0] for x in lines[2::4]]

lines = open('aircraft_code.txt','r').readlines()

iata = [x.split('\t')[0] for x in lines]
icao = [x.split('\t')[1] for x in lines]

for index,model in enumerate(plane_models):
    i = None

    try:
        i = iata.index(model)
    except  ValueError:
        try:
            i = icao.index(model)
        except  ValueError:
            pass
    
    print(i)
    


# pp.pprint(plane_models)