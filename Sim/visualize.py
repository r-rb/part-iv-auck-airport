import os
import simplekml
import datetime as dt
from plotly.offline import plot
import plotly.figure_factory as ff
import numpy as np
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

def gantt(start,finish,skip=1):
    df=[]
    for t,(st,fin) in enumerate(zip(start,finish)):
        for idx,(pl_st,pl_fin) in enumerate(zip(st,fin)):
            start_dt = minute2dt(skip*t+pl_st)
            end_dt = minute2dt(skip*t+pl_fin)

            if idx%4 == 0:
                res = 'Red'
            elif idx%4 == 1:
                res = 'Yellow'
            elif idx%4 == 2:
                res = 'Blue'
            else:
                res = 'Green'

            dt_str = '%Y-%m-%d %X'
            df.append(dict(Task="Minute "+str(skip*t), Start=start_dt.strftime(dt_str), Finish=end_dt.strftime(dt_str), Resource=res))
		
    colors = {'Red': 'rgb(220, 0, 0)',
                'Yellow': (1, 0.9, 0.16),
                'Green': 'rgb(0, 255, 100)',
                'Blue': 'rgb(40, 20, 255)'}

    plot(ff.create_gantt(df, colors=colors, index_col='Resource', group_tasks=True))
