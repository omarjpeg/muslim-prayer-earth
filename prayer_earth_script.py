
import numpy as np
import pandas as pd
import praytimes
import matplotlib.pyplot as plt
from datetime import date
import matplotlib.colors as mcolors
from mpl_toolkits.basemap import Basemap
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors
import imageio
from praytimes import PrayTimes
import warnings
warnings.filterwarnings("ignore")


# data = pd.read_csv('geonames-all-cities-with-a-population-1000.csv',sep=';')
#read the opendatasoft cities dataset

#splitting long&lat
# data[['Lat', 'Long']] = data['Coordinates'].str.split(',', 1, expand=True)


#get times for every one of the five daily prayers for each of the cities and put them into a dataframe
def rowfunc(x):
    global count
    times = PrayTimes().getTimes(date.today(), (float(x.Lat),float(x.Long)),0)
    for prayer,time in times.items():
        if prayer in ['fajr','dhuhr','asr','maghrib','isha']:
            if time!='-----':
                hrs,mins = time.split(':')
                x[prayer] = int(hrs)*60 + int(mins)
    return x

# data = data.apply(rowfunc,axis =1)
# data.to_csv('city_praytimes')

# ---- above data pre=procesing is optional and will take time, provided csv has the processed data ----

#return a nice UTC time string
def get_time_string(mins):
    hrs = int(np.floor(mins/60))
    mins = mins%60
    hourstring = None
    minstring = None
    if hrs<10:
        hourstring = f'0{hrs}'
    else:
        hourstring = str(hrs)
        
    if mins<10:
        minstring = f'0{mins}'
    else:
        minstring = str(mins)    
    return f'{hourstring}:{minstring} UTC'


#read saved csv
data = pd.read_csv('city_praytimes.csv')
plt.ion()
fig,ax0 = plt.subplots(figsize=(10,10))
ax0.set_position([0.0,0.0,1.0,1.0])
lat_viewing_angle = [20,20]
lon_viewing_angle = [-180,180]
rotation_steps = 1440
lat_vec = np.linspace(lat_viewing_angle[0],lat_viewing_angle[0],rotation_steps)
lon_vec = np.linspace(lon_viewing_angle[0],lon_viewing_angle[1],rotation_steps)
gif_indx = 0

m1 = Basemap(projection='ortho', 
          lat_0=lat_vec[0], lon_0=lon_vec[0],resolution=None) 
galaxy_image = plt.imread('black-galaxy-granite.jpg')
ax0.imshow(galaxy_image)
ax0.set_axis_off()
ax1 = fig.add_axes([0.25,0.25,0.5,0.5])

map_coords_xy = [m1.llcrnrx,m1.llcrnry,m1.urcrnrx,m1.urcrnry]
map_coords_geo = [m1.llcrnrlat,m1.llcrnrlon,m1.urcrnrlat,m1.urcrnrlon]

lat_vec = np.linspace(lat_viewing_angle[0],lat_viewing_angle[0],rotation_steps)
zoom_prop = 2.0 

gif_indx = 0
mks = 15

#custom legend and legend attributes, with markers for each prayer
legend_elements = [Line2D([0], [0],marker = 'o',lw=0, color=praycolors['fajr'], label='Fajr', markersize=mks),
                   Line2D([0], [0],marker = 'o', lw=0,color=praycolors['dhuhr'], label='Dhuhr', markersize=mks),
                   Line2D([0], [0],marker = 'o', lw=0,color=praycolors['asr'], label='Asr', markersize=mks),
                   Line2D([0], [0],marker = 'o', lw=0,color=praycolors['maghrib'], label='Maghrib', markersize=mks),
                    Line2D([0], [0],marker = 'o',lw=0, color=praycolors['isha'], label='Isha', markersize=mks)]

legend = ax0.legend(handles=legend_elements,
                    title="Prayer",fancybox = True,
                    handleheight=2.5,ncol=1,
                    labelspacing=0.1,loc=(.82,0.42))

plt.setp(legend.get_title(),fontsize='large')

ax0.text(x= np.sum(ax0.get_xlim())/2, y =60, s ='Muslim Prayer Times\nThroughout the Day',color = 'w',size =26, horizontalalignment='center', verticalalignment='center')
ax0.text(x= np.sum(ax0.get_xlim())/2, y =ax0.get_ylim()[0]-40, s ='By Omar A. Ibrahim\nwww.linkedin.com/in/omar-png/',color = 'w',size =13, horizontalalignment='center', verticalalignment='center',alpha = .85)

for pp in range(0,rotation_steps):
    ax1.clear()
    ax1.set_axis_off()
    m = Basemap(projection='ortho',resolution='l',
              lat_0=lat_vec[pp],lon_0=lon_vec[pp]+80,llcrnrx=-map_coords_xy[2]/zoom_prop,
                llcrnry=-map_coords_xy[3]/zoom_prop,urcrnrx=map_coords_xy[2]/zoom_prop,
                urcrnry=map_coords_xy[3]/zoom_prop, ax = ax1)
    for prayer in ['fajr','dhuhr','asr','maghrib','isha']:
        prayerattime= data.query(f'{prayer}=={pp}')
        xmap,ymap = m(np.array(prayerattime.Long), np.array(prayerattime.Lat))
        m.scatter(xmap,ymap , 15, marker='o', color=mcolors.to_rgb(praycolors[prayer]), zorder=3,alpha = .5)
    ax1.text(x= ax1.get_xlim()[1]-10, y =ax0.get_ylim()[0], s =get_time_string(pp),color = 'w',size =20, horizontalalignment='center', verticalalignment='center')
    m.bluemarble(scale=0.5)
#     m.drawcoastlines()
#     plt.show()

    fig.savefig(rf'.\temp{pp}.png', dpi=fig.dpi)
    plt.pause(0.01)
    gif_indx+=1


filenames = [rf'.\temp{i}.png' for i in range(0,rotation_steps)]
with imageio.get_writer(r'.\earth_prayer_movie.mp4', mode='I',fps = 60, quality=8, pixelformat='yuvj444p') as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)

