import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# spacing'      '
data = None
with open('./out.txt','r') as f:
    titles = ([],[],[])
    for i in range(0,3):
        x = f.readline()
        x = x.strip()
        titles[i].extend(x.split())
    list_titles  = [i+'_'+j+'_'+k for i,j,k in zip(*titles)]
    values_dict = {k:[] for k in list_titles}
    process = lambda x: x.strip().split()
    print(*list_titles)

    while True:
        line=f.readline()
        if not line: break
        li = process(line)
        for k,v in zip(list_titles,li):
            values_dict[k].append(float(v.strip('.')))
    data = values_dict

# V (B + P, R)
fuel_per_minute = [ x/y for x,y in zip(data["Cruise_Fuel_kg."],data["Cruise_Dist._min."])]

# R
dist = np.array(data["Block_Dist._nm."])

# without fuel (B+P)
mass = np.array([ d +  299000 for d in data["Payld_Mass_kg."]])

print(fuel_per_minute)


fig = plt.figure()
ax = Axes3D(fig)

ax.scatter(dist,mass,fuel_per_minute)

plt.show()


# first create a 
        
    #print(list_titles)