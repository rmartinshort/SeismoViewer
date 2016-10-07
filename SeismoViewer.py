#!/usr/bin/env python

#---------------
#RMS 2016
#---------------

#Program to quickly view and filter seismograms, found in the directory structure provided by obspyDMT

###
#Base class for SeismoViewer here
###

import os
import sys
import obspy 
import glob
import Tools
from operator import itemgetter
import numpy as np
from scipy.stats import mode

#for timing various aspects of this code
from time import time


class SeismoView:
	def __init__(self,datadirectory,extension='BHZ',multiplot=True):

	    #location of the event directories
		self.datadirectory = datadirectory

		#file type of interest
		self.fileextension = extension

	    #do we want to plot multiple records (usually, yes)
		self.multiplot = multiplot

	    #number of records we want to plotm default is all
		self.records = 'all'

        #keep track of the array that we will eventually write to file
		self.arraylen = 0

		self.filterslicestreamdata = None

		isdata = self.checkfordata()

		if isdata == False:
			print 'File struture in %s is not correct. Need to provide path to data directory containing SAC files' %self.datadirectory
			sys.exit(1)

	def checkfordata(self):

		'''Checks that SAC files are present in the directory that was provided'''

		cwd = os.getcwd()

		try:
			os.chdir(self.datadirectory)
		except:
			os.chdir(cwd)
			return False

		if self.fileextension:
			SACfiles = glob.glob('*.%s' %self.fileextension)
			if len(SACfiles) == 0:
				os.chdir(cwd)
				return False

		os.chdir(cwd)

		return True

	def multiload(self):

		'''Load all traces into an obspy stream object, in order of distance'''

		self.datastream = obspy.Stream()

		self.SACfiles=glob.glob('%s/*.%s' %(self.datadirectory,self.fileextension))

		#print self.SACfiles

		#get the distances from the SACfiles and order them for distance

		t0 = time()
		for sacfile in self.SACfiles:
			st = obspy.read(sacfile,format='SAC')
			self.datastream += st[0]

		self.datastream = Tools.orderstream(self.datastream)

		#May be necessary to decimate in order to same time
		#self.datastream.decimate(factor=2)

		t1 = time()


		print 'Load time = %g' %(t1-t0)

	def preservetraces(self):

		'''Use instead of slicing - keeps the whole trace. Slow but can be used for debugging'''

		self.slicestream = self.datastream

		self.slicestream.normalize()

		lentraces = []

		for trace in self.slicestream:

			lentraces.append(len(trace.data))

		self.arraylen = max(lentraces)



	def slicetraces(self,phase='P',halfwindow=20):

		'''Makes a new stream consisting of traces cut around predicted arrival given by phase, with a halfwindow
		provided by the user'''

		self.slicestream = obspy.Stream()

		#keep track of the trace lengths
		lentraces = []

		t0 = time()

		for trace in self.datastream:

			if phase == 'P':

				try:
					Phasetime = trace.stats.sac.user1

					if Phasetime < 0.0: #probably means that Ptime had not been added to the SAC header - check that the data has been properly processed
						Phasetime = 0.0
				except:
					print 'No P arrival found for trace %s' %trace[0]
					Phasetime = 0.0

			if phase == 'S':

				try:
					Phasetime = trace.stats.sac.user2

					if Phasetime < 0.0: #probably means that Ptime had not been added to the SAC header - check that the data has been properly processed
						Phasetime = 0.0
				except:
					print 'No S arrival found for trace %s' %trace[0]
					Phasetime = 0.0


			if Phasetime != 0:

				starttime = obspy.UTCDateTime(trace.stats.starttime)
				endtime = obspy.UTCDateTime(trace.stats.endtime)

				duration = endtime-starttime
				#print 'Duration: %g' %duration

				#Check that the trace is long enough to slice
				if duration <= Phasetime + halfwindow:
					print 'Error! Trying to slice beyond the end of the trace!'
				else:
					slicetrace = trace.slice(starttime+Phasetime-halfwindow,starttime+Phasetime+halfwindow)
					slicetrace.stats.sac.user3 = halfwindow
					self.slicestream += slicetrace
					lentraces.append(len(slicetrace.data))

			self.slicestream.normalize()

			#Having a detrend here increases run times dramatically 
			#self.slicestream.detrend()

			self.arraylen = max(lentraces)

		t1 = time()

		print 'slice time = %g' %(t1-t0)





	def filterslicestream(self,f1,f2):

		'''bandpass slicestream according to user input'''


		self.filterslicestreamdata = Tools.filterstream(self.slicestream.copy(),f1,f2)
		self.filterslicestreamdata.detrend('simple')
		self.filterslicestreamdata.normalize()



	def arraytracesave(self,outfilebasename,phase='P'):

		'''Saves the stream data in .npy format'''

		#get the length of a trace and use it to generate a matrix of tracedata

		#  --> traces (in order of distance from source)
		#  |
		#  |
		#  |
		#  data 


		#This requires all the traces to be of the same length. Since they've all been sliced, this should be the case

		#Make a copy of the memory stream, to be written to an outfile, ready for plotting

		if self.filterslicestreamdata:
			outstream = self.filterslicestreamdata
		else:
			outstream = self.slicestream


		samples = self.arraylen
		print samples
		traces = len(outstream)


		txtfile = outfilebasename+'.dat'
		outfile = open(txtfile,'w')

		#Get information about the event
		quakelon = outstream[0].stats.sac.evlo
		quakelat = outstream[0].stats.sac.evla
		quakedeph = outstream[0].stats.sac.evdp
		quakemag = outstream[0].stats.sac.mag

		outfile.write('---------------------------------\n')
		outfile.write('Quake information below:\n')
		outfile.write('%g %g %g %g\n' %(quakelon,quakelat,quakedeph,quakemag))
		outfile.write('---------------------------------\nTrace information below\n')
		outfile.write('Network Station Channel\n')

		arr = np.zeros([samples,traces])

		shapearr = np.shape(arr)

		for i in range(shapearr[1]-1):

			#information associated with the trace (for writing to file)
			trace = outstream[i]

			network = trace.stats.network
			station = trace.stats.station
			channel = trace.stats.channel
			delta = trace.stats.delta

			dbshearpick = trace.stats.sac.user4

			if phase == 'P':
				phasetime = trace.stats.sac.user1
			elif phase == 'S':
				phasetime = trace.stats.sac.user2
			else:
				print 'Phase %s not recognized' %phase 
				sys.exit(1)

			arr[:len(outstream[i].data),i] = outstream[i].data

			samp = trace.stats.npts
			halfwindow = trace.stats.sac.user3

			outfile.write('%s %s %s %s %s %s %s %s\n' %(network,station,channel,phasetime,halfwindow,samp,delta,dbshearpick))

		outfile.close()

		np.save(outfilebasename+'.npy',arr)



if __name__ == '__main__':

	'''Testing'''


	testdir = '/Users/rmartinshort/Documents/Berkeley/SeismoGramManip/test_data/2016-01-01_2016-01-25/20160107_23/BH_VEL'

	test = SeismoView(testdir)
	test.multiload()
	test.slicetraces(phase='P')
	test.filterslicestream(2,5)
	#test.filterwholestream(2,10)
	test.arraytracesave('testdataset')













