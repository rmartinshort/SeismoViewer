#!/usr/bin/env python 

#---------------
#RMS 2016
#---------------

#Program to quickly view and filter seismograms, found in the directory structure provided by obspyDMT

#functions for making station-event maps


from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import obspy
import os
import sys
import glob
import numpy as np

def StationEventsMap(stlats,stlons,evlat,evlon,stdists,stnames):

	'''Plot a map of just one event and the stations at which it was recorded'''


	#print stlats,stlons,evlat,evlon,stdists,stnames
	print 'Event coordinates: %g %g' %(evlat,evlon)

	alaskamap = Basemap(width=2600000,height=2100000,resolution='l',projection='aea',lat_1=54.0,lat_2=69.0,lon_0=-150,lat_0=64)
	alaskamap.fillcontinents()
	alaskamap.drawcountries()
	alaskamap.drawcoastlines(linewidth=0.1)
	alaskamap.drawmapscale(-145, 58, -145, 58, 400)

	alaskamap.drawparallels(np.arange(-90,90,5),labels=[1,1,0,0],linewidth=0.5,fontsize=10)
	alaskamap.drawmeridians(np.arange(-180,180,10),labels=[0,0,0,1],linewidth=0.5,fontsize=10)

	xev,yev = alaskamap(evlon, evlat)
	xst,yst = alaskamap(stlons, stlats)

	for i in range(len(stnames)):
		plt.text(xst[i]-10000,yst[i]+10000,'%s' %stnames[i])
		alaskamap.drawgreatcircle(evlon,evlat,stlons[i],stlats[i],linewidth=0.5,color='b')


	alaskamap.plot(xev,yev,'r*',markersize=12)
	alaskamap.plot(xst,yst,'g^',markersize=8)



	plt.show()



def Alaskamapfull(path):

	'''Make map of all station/event pairs in a particular project. Path is to the uppermost directory'''

	eventIDS = glob.glob('%s/20*' %path)

	if len(eventIDS) == 0:
		print 'Cannot find any events in path %s' %path
		sys.exit(1)

	evlats = []
	evlons = []
	stlats = []
	stlons = []
	stanames = []

	for event in eventIDS:

		if os.path.isdir('%s/BH_VEL' %event):

			sacfiles = glob.glob('%s/BH_VEL/*HZ' %event) #just get all the vertical component files 

		else:

			sacfiles = glob.glob('%s/BH_RAW/*HZ' %event) #just get all the vertical component files


		if len(sacfiles) == 0:
			print 'No sacfiles found in %s' %event

		tr1 = obspy.read(sacfiles[0],format='SAC')
		evlons.append(tr1[0].stats.sac.evlo)
		evlats.append(tr1[0].stats.sac.evla)


		for sacfile in sacfiles:

			stname = sacfile.split('/')[-1].split('.')[1]

			if stname not in stanames:

				stanames.append(stname)
				tr = obspy.read(sacfile,format='SAC')
				stlons.append(tr[0].stats.sac.stlo)
				stlats.append(tr[0].stats.sac.stla)


	alaskamap = Basemap(width=2600000,height=2000000,resolution='l',projection='aea',lat_1=54.0,lat_2=69.0,lon_0=-150,lat_0=63)
	alaskamap.fillcontinents()
	alaskamap.drawcountries()
	alaskamap.drawcoastlines(linewidth=0.1)
	alaskamap.drawmapscale(-145, 59, -145, 59, 400)

	alaskamap.drawparallels(np.arange(-90,90,5),labels=[1,1,0,0],linewidth=0.5,fontsize=10)
	alaskamap.drawmeridians(np.arange(-180,180,10),labels=[0,0,0,1],linewidth=0.5,fontsize=10)
	#alaskamap.arcgisimage(service='NatGeo_World_Map',verbose=False,xpixels=600)

	xev,yev = alaskamap(evlons, evlats)
	alaskamap.plot(xev,yev,'r*',markersize=8)

	xst,yst = alaskamap(stlons, stlats)
	alaskamap.plot(xst,yst,'g^',markersize=8)

	plt.show()





	plt.show()

if __name__ == '__main__':

	Alaskamapfull('/Users/rmartinshort/Documents/Berkeley/SeismoGramManip/test_data/autopicking_1/BOX/Merged/2015-10-01_2016-10-01')


