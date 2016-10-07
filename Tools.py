#!/usr/bin/env python

########################
#A collection of tools for use with SeismoViewer
########################

import obspy 
from obspy.core.util import locations2degrees
from obspy import UTCDateTime
import sys
from operator import itemgetter

def orderstream(instream):

	'''Puts the objects in a stream in order of distance. Faster than getdistance function'''

	diststream = obspy.Stream()
	dists = {}

	for trace in instream:
		dist = trace.stats.sac.dist
		dists[trace] = dist

	for item in sorted(dists.items(), key=itemgetter(1)):
		diststream += item[0]

	return diststream


def getdistance(intrace):

	'''Extract great circle arc distance from station to event'''

	try:
		distdegree = intrace.stats.sac.gcarc
		return distdegree
	
	except:

		stalat = intrace.stats.sac.stla
		stalon = intrace.stats.sac.stlo
		eventlat = intrace.stats.sac.evla
		eventlon = intrace.stats.sac.evlo
		eventdepth = intrace.stats.sac.evdp
		#calculate distance to quake in degrees
		distdegrees = locations2degrees(stalat,stalon,eventlat,eventlon)

		return distdegree

	print 'Error: intrace object not readable'
	sys.exit(1)


def filterstream(instream,bplow,bphigh):

	'''Bandpass filter the trace between the provided limits'''

	instream.filter("bandpass",freqmin=bplow,freqmax=bphigh,corners=2,zerophase=True)

	return instream


def extractphases(intrace,distonly=False):
	'''Extract information about phases from SAC header information, and station-event distances'''

	distdegree = getdistance(intrace)

	if distonly:
		return distdegree

	else:

		offset = intrace.stats.sac.o
		network = intrace.stats.network
		station = intrace.stats.station
		channel = intrace.stats.channel
		starttime = UTCDateTime(intraceobj.stats.starttime)
		endtime = UTCDateTime(intraceobj.stats.endtime)

		try:
			Ptime = intraceobj.stats.sac.user1

			if Ptime < 0.0: #probably means that Ptime had not been added to the SAC header - check that the data has been properly processed
				Ptime = 0.0
		except:
			print 'No P arrival found in the SAC header'
			Ptime = 0.0
		try:
			Stime = intraceobj.stats.sac.t2
			if Stime < 0.0:
				Stime = 0.0 
		except:
			print 'No S time found in SAC header'
			Stime = 0.0


		return [distdegrees,Ptime,Stime,network,station,channel,starttime,endtime,offset]