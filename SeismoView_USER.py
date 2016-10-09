#!/usr/bin/env python

#---------------
#RMS 2016
#---------------

#Program to quickly view and filter seismograms, found in the directory structure provided by obspyDMT

#User loop of the Seismoviewer program 

import os
import sys 
import glob
import argparse
from SeismoViewer import SeismoView
import time
 


parser = argparse.ArgumentParser()
parser.add_argument('-path',action='store',dest='inputpath',help='The full file path to the data you want to prepare for a tomography project')
parser.add_argument('-phase',action='store',dest='phase',help='The seismic phase you are interested in: This determines which SAC files are accessed and what the final output is. Choose from S or P')
parser.add_argument('-cleanup',action='store_true',dest='cleanup',help='If set, output files from the program will be deleted when it ends')
parser.add_argument('-fulltrace',action='store_true',dest='fulltrace',help='If set, the program will plot the entire trace, otherwise it will slice around the arrival of interest')
results = parser.parse_args()


#may want to run the viewer in various modes - possibly to control the length of the traces that are displayed etc

def userloop(path,ph,fulltrace=None):

	''' User decisions about how to manipulate the data '''

	#Get the eventID
	eventID = path.split('/')[-2]
	print eventID

	#Load the data into a Seimoview object
	SV = SeismoView(path)
	SV.multiload()

	#Don't necessarily need to use this option, but there for now
	#print fulltrace

	if fulltrace:
		SV.preservetraces()
	else:
		SV.slicetraces(phase=ph)

	#define filter bands
	filterbands = None


	#Now the user decides what to do with it

	while 1:

		usercommand = raw_input('SV>: ')

		#exit command

		if usercommand == 'q':
			sys.exit(1)

		elif usercommand == 'n':

			return None

		#plot command 

		elif usercommand == 'p':

			if filterbands:
				basename = '%s_%s_%s_data' %(eventID,b1,b2)
			else:
				basename = '%s_data' %eventID

			#Save the data components to be plotted
			SV.arraytracesave(basename)

			#Run the plotting command - the prompt will be freed again once the user quits the plot

			#This one is for full seismogram plotting

			if fulltrace:
				os.system('./plot_quakes_full.py %s %s' %(basename+'.npy',basename+'.dat'))
			else:
				os.system('./plot_quakes_sliced.py %s %s' %(basename+'.npy',basename+'.dat'))

		#flag command - creates or appends to a file containing flagged events 

		elif usercommand[:4] == 'flag':

			outfilename = 'Flagged_events_'+path.split('/')[-3]+'.dat'
			now = time.strftime("%c")

			#Append flag time, event name and user comments to the file 

			if os.path.isfile(outfilename):

				outfile = open(outfilename,'a')
				outfile.write(now)
				outfile.write('\n')
				outfile.write('%s %s\n' %(eventID,usercommand))
				outfile.close()

			else:

				outfile = open(outfilename,'w')
				outfile.write(now)
				outfile.write('\n')
				outfile.write('%s %s\n' %(eventID,usercommand))
				outfile.close()

		# go to another event name

		elif usercommand[:2] == 'ID':

			IDname = usercommand.split()[1]
			print 'Going to event %s' %IDname

			return IDname

       
        #filter command

		elif usercommand[:2] == 'bp':

			try:
				command = usercommand.split()
				b1 = float(command[1])
				b2 = float(command[2])

				if b2 <= b1:
					print 'filter band b2 cannot be larger than b1'
				else:
					filterbands=True
					print 'filtering'
					SV.filterslicestream(b1,b2)

			except:
				print 'filter command %s not recognized' %usercommand


		elif usercommand == 'map':

			#Makes a station-event map for this configuration, with the distances 

			print '---------------------------------'
			print 'Making station-event map'
			print '---------------------------------'


			SV.map_event_stations()

		else:

			print 'Command not recognized'



def main():

	cwd = os.getcwd()

	path = results.inputpath
	phase = results.phase
	clean = results.cleanup
	fulltrace = results.fulltrace
	print fulltrace

	if (phase != 'P'):
		print 'input phase %s not recognized' %phase

	if not os.path.isdir(path):
		print 'Input directory %s not found' %path
		sys.exit(1)

	events = glob.glob('%s/20*' %path)

	if len(events) == 0:
		print 'Cound not find any event directories in folder %s' %path
		sys.exit(1)
		
	print '\n------------------------\n'
	print 'Found %g events' %len(events)
	print '\n------------------------\n'

	newevent = None

	for event in events:

		if os.path.isdir('%s/BH_VEL' %event):

			print 'Found BH_VEL'

			if newevent:

				IDname = userloop('%s/BH_VEL' %newevent,phase,fulltrace=fulltrace)
				newevent = None

			else:

				IDname = userloop('%s/BH_VEL' %event,phase,fulltrace=fulltrace)

			if IDname:
				neweventparths = event.split('/')
				neweventparths[-1] = IDname
				newevent = '/'.join(neweventparths)

			if clean:
				print 'Cleanup -- removing .npy and .dat files'
				os.system('rm -rf *_data.npy *_data.dat')

		elif os.path.isdir('%s/BH_RAW' %event):

			print 'Found BH_RAW'

			if newevent:

				IDname = userloop('%s/BH_RAW' %newevent,phase,fulltrace=fulltrace)
				newevent = None

			else:

				IDname = userloop('%s/BH_RAW' %event,phase,fulltrace=fulltrace)

			if IDname:
				neweventparths = event.split('/')
				neweventparths[-1] = IDname
				newevent = '/'.join(neweventparths)

			if clean:
				print 'Cleanup -- removing .npy and .dat files'
				os.system('rm -rf *_data.npy *_data.dat')

		else:
			print 'No viable data directory found in event %s' %event



if __name__ == '__main__':

	main()



