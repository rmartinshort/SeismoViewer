#!/usr/bin/env python

#Some basic pyqtgraph plotting tests

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import sys

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


quakedata = lines[2].split()
evlon = quakedata[0]
evlat = quakedata[1]
evdep = float(quakedata[2])/1000.0
evmag = quakedata[3]

stationdata = lines[6:]

#Set up the QTGui app
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="SeismoViewer plot")

win.setWindowTitle('Event: LON %s LAT %s DEPTH %g MAG %s ID ' %(evlon,evlat,evdep,evmag))

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

for i in range(np.shape(seisarr)[1]-1):

	if (i>0) and (i%2 == 0):
		win.nextRow()

	stavals = stationdata[i].split()
	network = stavals[0]
	station = stavals[1]
	channel = stavals[2]
	ptime= float(stavals[4])
	npts = int(stavals[5])
	x = np.linspace(0,ptime*2,npts)

	p1 = win.addPlot(title="%s %s %s" %(network,station,channel))
	p1.plot(x,seisarr[:len(x),i], pen=(255,0,0))
	p1.plot([ptime,ptime],[min(seisarr[:,i]),max(seisarr[:,i])],pen=(0,255,0),name='Pick')
	p1.setLabel('bottom', "Time", units='s')
	p1.showAxis('left', False)

win.resize(1200,600)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


