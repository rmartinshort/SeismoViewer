#!/usr/bin/env python

#Some basic pyqtgraph plotting tests

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import sys
from time import time

dataarray = sys.argv[1]
metadata = sys.argv[2]


#Read the data into memory
try:
	seisarr = np.load(dataarray)
except:
	print 'Cannot read input array file %s' %dataarray
	sys.exit(1)
try:
	infile = open(metadata,'r')
	lines = infile.readlines()
	infile.close()
except:
	print 'Cannot read metadata file %s' %metadata


evID = dataarray.split('/')[0].split('_')[0]

quakedata = lines[2].split()
evlon = quakedata[0]
evlat = quakedata[1]
evdep = float(quakedata[2])/1000.0
evmag = quakedata[3]

stationdata = lines[6:]

#Set up the QTGui app
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="SeismoViewer plot")
#win.resize(1200,600)
win.setWindowTitle('SeismoViewer')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p1 = win.addPlot(title='Event: LON %s LAT %s DEPTH %g MAG %s ID %s' %(evlon,evlat,evdep,evmag,evID))
#p1.addLegend()
#p2.plot(np.random.normal(size=100), pen=(255,0,0), name="Red curve")
#p2.plot(np.random.normal(size=110)+5, pen=(0,255,0), name="Blue curve")
#p2.plot(np.random.normal(size=120)+10, pen=(0,0,255), name="Green curve")


t0 = time()

inc = 0
for i in range(np.shape(seisarr)[1]-1):
	print i

	stavals = stationdata[i].split()
	network = stavals[0]
	station = stavals[1]
	channel = stavals[2]

	ptime= float(stavals[4]) #this is actually the 'halfwindow' value, where the arrival has been picked 
	npts = int(stavals[5])
	delta = float(stavals[6])
	dbpick = float(stavals[7])
	distance = float(stavals[8])/1000.0

	#only plot the events with picks(?)


	if dbpick > 0:
		res = float(stavals[3])-dbpick #raveltime residual between predicted and actual arrival
		pick = ptime - res



	x = np.linspace(0,ptime*2,npts)
	p1.plot(x,seisarr[:len(x),i]+inc, pen=(255,0,0))
	#p1.plot([ptime,ptime],[min(seisarr[:,i])+inc,max(seisarr[:,i])+inc],pen=(0,255,0))
	p1.plot([pick,pick],[min(seisarr[:,i])+inc,max(seisarr[:,i])+inc],pen=(0,0,225))

	text1 = pg.TextItem('%s %s %s' %(network,station,channel))
	#include the event-station distance
	text2 = pg.TextItem('%s km' %distance)
	p1.addItem(text1)
	p1.addItem(text2)
	text1.setPos(0, inc)
	text2.setPos(ptime*1.5,inc)

	inc += 1

t1 = time()


p1.setLabel('bottom', "Time", units='s')
p1.showAxis('left', False)

print 'Time to load plot: %g' %(t1-t0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


