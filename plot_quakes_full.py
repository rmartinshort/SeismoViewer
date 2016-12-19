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
evdep = float(quakedata[2])
evmag = quakedata[3]

stationdata = lines[6:]

#Set up the QTGui app
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="SeismoViewer plot")
#win.resize(1200,600)
win.setWindowTitle('SeismoViewer')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p1 = win.addPlot(title='Event: LON %s LAT %s DEPTH %g km MAG %s ID %s' %(evlon,evlat,evdep,evmag,evID))
#p1.addLegend()
#p2.plot(np.random.normal(size=100), pen=(255,0,0), name="Red curve")
#p2.plot(np.random.normal(size=110)+5, pen=(0,255,0), name="Blue curve")
#p2.plot(np.random.normal(size=120)+10, pen=(0,0,255), name="Green curve")

#Get basic information required to plot
stvals = stationdata[0].split()
npts = float(stvals[5])
delta = float(stvals[6])
#Make x axis array for the plotting 
x = np.linspace(0,npts*delta,npts)

t0 = time()

inc = 0
for i in range(np.shape(seisarr)[1]-1):

	stavals = stationdata[i].split()
	network = stavals[0]
	station = stavals[1]
	channel = stavals[2]
	ptime= float(stavals[3])
	dbpick = float(stavals[7])
	distance = float(stavals[8])/1000.0
	sacpick = float(stavals[9])
	pythonpick = float(stavals[10])

	if abs(sacpick-ptime) > 2:
		sacpick = 0
	if abs(pythonpick-ptime) > 2:
		pyqtgraph = 0

	#only plot events that have picks, which saves time

	if dbpick > 0:

		#p1.plot(x,seisarr[:len(x),i]+inc, pen=(255,0,0))
		p1.plot(x,seisarr[:len(x),i]+inc, pen=(255,0,0))

		#plot the P wave arrival times 
		p1.plot([ptime,ptime],[min(seisarr[:,i])+inc,max(seisarr[:,i])+inc],pen=(0,255,0))

		#plot the pick produced by dbshear, if it exists
		p1.plot([dbpick,dbpick],[min(seisarr[:,i])+inc,max(seisarr[:,i])+inc],pen=(0,0,255))

		#plot the pick produced by sac, if it exists
		p1.plot([sacpick,sacpick],[min(seisarr[:,i])+inc,max(seisarr[:,i])+inc],pen=(255,255,255))

		#plot the pick produced by sac, if it exists
		p1.plot([pythonpick,pythonpick],[min(seisarr[:,i])+inc,max(seisarr[:,i])+inc],pen=(255,0,0))

		text1 = pg.TextItem('%s %s %s' %(network,station,channel))

		#include the event-station distance
		text2 = pg.TextItem('%s km' %distance)
		p1.addItem(text1)
		p1.addItem(text2)
		text1.setPos(0, inc)
		text2.setPos(100,inc)
		inc += 2

t1 = time()

print 'Time to load plot: %g' %(t1-t0)

p1.setLabel('bottom', "Time", units='s')
p1.showAxis('left', False)




## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


