import os
import simplekml
import datetime as dt
from plotly.offline import plot
import plotly.figure_factory as ff
import numpy as np
from random import seed, random
from subprocess import DEVNULL, STDOUT, check_call

MIN_PER_HOUR = 60
SEC_PER_MIN = 60
kml_name = "sim.kml"

def visualize(kml):
    kml.save(kml_name)

    # with open(os.devnull, 'wb') as devnull:
    # 	check_call(['gnome-maps', kml_name], stdout=DEVNULL, stderr=STDOUT)

def minute2dt(minute,year = 2018,month=9,day=4):
    hour = int(minute / MIN_PER_HOUR)
    minute -= hour*MIN_PER_HOUR
    second = int((minute * SEC_PER_MIN) % SEC_PER_MIN)
    minute = int(np.floor(minute))
    return dt.datetime(year,month,day,hour,minute,second)

def gantt(start,finish,name,skip=1):
    df=[]
    colors = {}
    for t,(st,fin,nm) in enumerate(zip(start,finish,name)):
        for pl_st,pl_fin,n in zip(st,fin,nm):
            start_dt = minute2dt(skip*t+pl_st)
            end_dt = minute2dt(skip*t+pl_fin)

            if n not in colors:
                seed(n)
                clr = "rgb("+str(255*random())+","+str(255*random())+","+str(255*random())+")"
                colors[n] = clr

            dt_str = '%Y-%m-%d %X'
            df.append(dict(Task="Minute "+str(skip*t), Start=start_dt.strftime(dt_str), Finish=end_dt.strftime(dt_str), Resource=n))

    plot(ff.create_gantt(df, colors=colors, index_col='Resource', show_colorbar=True, group_tasks=True,showgrid_x=True))
