# Thia python program is used to read individual pairs of data files from 
# ANTARES Temperature logger attached to the top and bottom of the Thermal Blanket 
# heat flow instrument
#
# See Salmi et al., 2014 for a more detailed description of the Thermal Blanket
# 
# Data should be downloaded from the sensor to a *.dat file.
#
# Required files for processing:
# - Top thermistor temperature *.dat file
# - Bottom thermistor temperature *.dat file
# - meta data csv file 
# 
# Processing steps:
# 1) Data is loaded from both the top and bottom logger *.da tfiles
# 2) A precalculated offset calibration is applied to zero to remove all individual bias
# 3) All data is written out to a 'Golden Nugget'
# 4) Essential data (such as temperature records and time) are written to a matlab *mat file
#    for easy loading into matlab
#
# Each blanket was used at multiple heat flow stations. Station data are in
# the *.csv file for the corresponding blanket letter.
#
#
# Usage: 
#     	python Generate_GoldenNugget.py top_blanket_temp.dat bot_blanket_temp.dat Blanket_Deployment_Meta.csv
#
# Example *.dat file format from ANTARES logger:
#
#######################################################################
##
## LoggerIdentifier    : 0000014
## Comment             : 
## PC Time             : 24 August 2011 , 00:06:05
## Logger Time         : 24 August 2011 , 00:05:49
## StartBatteryVoltage :      2970 mV
## EndBatteryVoltage   :      2928 mV
## TotalSampleCount    :    113908
## ResistanceOffset    :     11913.96429
## ResistanceScale     :     90906.90354
## TemperatureOffset   :         0.0010743547
## TemperatureLinear   :         0.0002113377
## TemperatureCubic    :         0.0000000922
##
#######################################################################
#2003 07 16 15 00 04    32114    45981.044       16.088
#2003 07 16 15 00 08    32115    45982.617       16.087
# ...
#
# This code is based on a collection of matlab functions written by M. Hutnak. 

# Import packages
import os.path
import sys
import datetime
from datetime import date
import numpy as np
import scipy.io
import matplotlib.pyplot as plt
import csv

# Modules
########################################################
def FindOffset(filename):  
	
	if len(filename) <= 0:
		print(' No filename!')
		exit()
	elif len(filename) >= 7:		# Some antares datalogger ID's have characters on the end, others do not.	
		filename = filename[0:7]    # If it has a character, remove it in order to match ID with offset
		
		LoggerNumber = {}
		offset_file = csv.reader(open('offsets.csv', 'r'))

		for row in offset_file: 
			LoggerNumber[row[0]] = float(row[1])
	
	if filename in LoggerNumber:
		offset = LoggerNumber[filename]
		print(" Found offset for this thermistor of %1.4f" % offset)
		return offset
	else:
		L= (" Could not find offset for thermistor: ",filename)
		print(''.join(L))
		
##########################################################
# Start of main program
#
# section that if input parameters are incorrect, will respond with a help section
#			potentially use argparse for this but at a later date

file_top = sys.argv[1]
file_bot = sys.argv[2]

# Confirm that the files exist in the current director
if os.path.isfile(file_top):
	fid0 = open(file_top)	
else: 
	L = ["Unable to open file: ", file_top]
	print(''.join(L))
	exit()

if os.path.isfile(file_bot):
	fid1 = open(file_bot)
else: 
	L = ["Unable to open file: ", file_bot]
	print(''.join(L))
	exit()

# Now working on the top file - Loading and adjusting for offset	
firstline = fid0.read(71)		     # Reading in the first line 

print(' Verifying that top file is an Antares file')
if firstline == '######################################################################\n':
	print(' YES: This is an antares file')
	print(' ')
	fid0.seek(0,0)
	total_length = len(fid0.read())//54
	fid0.seek(0,0)
	
	# Initalized variables here
	tyr = [];
	tmo= [];
	tdy = [];
	thr = [];
	tmn = [];
	tsec = [];
	traw = [];
	tres = [];
	tdeg = [];
	
	# Read in the header and data
	for i in range(0,total_length):
		text = fid0.readline()
		if len(text) == 0:
			break

		if i == 2:
			tfilename = text[24:31]
		if i > 15:
			tyr.append(text[0:4])
			tmo.append(text[5:7])
			tdy.append(text[8:10])
			thr.append(text[11:13])
			tmn.append(text[14:16])
			tsec.append(text[17:19])
			traw.append(text[23:28])
			tres.append(text[32:41])
			tdeg.append(text[48:54])
	
	# Convert everything to arrays
	tyr = np.array(tyr, dtype='float32')
	tmo = np.array(tmo, dtype='float32')
	tdy = np.array(tdy, dtype='float32')
	thr = np.array(thr, dtype='float32')
	tmn = np.array(tmn, dtype='float32')
	tsec = np.array(tsec, dtype='float32')
	traw = np.array(traw, dtype='float32')
	tres = np.array(tres, dtype='float32')
	tdeg = np.array(tdeg, dtype='float32')
				
	L = [" Top Logger ID: ", tfilename]
	print(''.join(L))
	print(' ')
	
	print(' Getting Top Thermistor Offset...')
	tdeg_offset = FindOffset(tfilename)
	
	#from Antares_Offset_Value import offset
	print(" Imported %1.4f" % tdeg_offset)
	print(' *************************** ')
	fid0.close()
else:
	print(' NO: This is NOT an antares file ')
	print(' Check that the file is the output of Antaries software')
	exit()
	
#Now working on the Bottom thermistor file		
firstline = fid1.read(71)

print(' Verifying that the bottom file is an Antares file')
if firstline == '######################################################################\n':
	print(' YES: This is an antares file')
	print(' ')
	fid1.seek(0,0)
	total_length = len(fid1.read())//54
	fid1.seek(0,0)

	# Initalized variables here
	byr = []
	bmo = []
	bdy = []
	bhr = []
	bmn = []
	bsec = []
	braw = []
	bres = []
	bdeg = []
	
	# Read in the header
	for i in range(0,total_length):
		text = fid1.readline()
		if len(text) == 0:
			break

		if i == 2:
			bfilename = text[24:31]
		if i > 15:
			byr.append(text[0:4])
			bmo.append(text[5:7])
			bdy.append(text[8:10])
			bhr.append(text[11:13])
			bmn.append(text[14:16])
			bsec.append(text[17:19])
			braw.append(text[23:28])
			bres.append(text[32:41])
			bdeg.append(text[48:54])
			
	# Convert everything to arrays
	byr = np.array(byr, dtype='float32')
	bmo = np.array(bmo, dtype='float32')
	bdy = np.array(bdy, dtype='float32')
	bhr = np.array(bhr, dtype='float32')
	bmn = np.array(bmn, dtype='float32')
	bsec = np.array(bsec, dtype='float32')
	braw = np.array(braw, dtype='float32')
	bres = np.array(bres, dtype='float32')
	bdeg = np.array(bdeg, dtype='float32')
	L = [" Bottom Logger ID: ", bfilename]
	print(''.join(L))
	print(' ')
	
	print(' Getting Bottom Thermistor Offset...')
	bdeg_offset = FindOffset(bfilename)
	
	fid1.close()
else:
	print(' NO: This is NOT an antares file ')
	exit()

# Covert the time into 'matlab format'
# Time is in matlab datenum format (Julian Day) for easy comparison 
# and conversion between various formats.
# 719529 = datenum(1970,1,1,0,0,0)

btime = []
ttime = []
for i in range(0,len(byr)): 	# !! NOTE: There is a very slight rounding error of 0.0001 sec
	timebase = date.toordinal(date(int(byr[i])+1,int(bmo[i]),int(bdy[i])))
	dum = float(timebase) + (int(bhr[i])+(int(bmn[i])+int(bsec[i])/60.0)/60.0)/24.0
	btime.append(dum)
	
for i in range(0,len(tyr)):
	timebase1 = date.toordinal(date(int(tyr[i])+1,int(tmo[i]),int(tdy[i])))
	dum1 = float(timebase1) + (int(thr[i])+(int(tmn[i])+int(tsec[i])/60.0)/60.0)/24.0
	ttime.append(dum1)

btime = np.array(btime, dtype='float64')
ttime = np.array(ttime, dtype='float64')

if btime.size != ttime.size:
	print(' Timing is off. Reconciling times between top and bottom thermistors.')

# Some Quality Control
C = np.intersect1d(btime,ttime)
B_diff = np.in1d(btime,C)
T_diff = np.in1d(ttime,C)

btime = btime[B_diff]
byr  = byr[B_diff]
bmo  = bmo[B_diff]
bdy  = bdy[B_diff]
bhr  = bhr[B_diff]
bmn  = bmn[B_diff]
bsec = bsec[B_diff]
braw = braw[B_diff]
bres = bres[B_diff]
bdeg = bdeg[B_diff]

ttime=ttime[T_diff]
tyr  = tyr[T_diff]
tmo  = tmo[T_diff]
tdy  = tdy[T_diff]
thr  = thr[T_diff]
tmn  = tmn[T_diff]
tsec = tsec[T_diff]
traw = traw[T_diff]
tres = tres[T_diff]
tdeg = tdeg[T_diff]

# Apply offsets to the Temperatures
tdeg_corrected = tdeg-tdeg_offset
bdeg_corrected = bdeg-bdeg_offset

#fig = plt.figure()
#Bot, = plt.plot(btime,bdeg_corrected,'r--',label='Bottom Corrected')
#Top, = plt.plot(ttime,tdeg_corrected,'b--',label='Top Corrected')
#plt.xlabel('Julian Day (datenum)')
#plt.ylabel('Temperature (deg C)')
#plt.legend(handles=[Bot,Top]);
#plt.show()

# Get the individual deployment meta data from csv file that should be in the current folder
if __name__ == '__main__':
	try:
		CSVfile = sys.argv[3]
	except IndexError:
		CSVfile = ""
		print(" Unknown Time file!")
		exit()

latdeg = []
latmin = []
londeg = []
lonmin = []
blanket = []
divenumber = []
deploy = []
jdaydep = []
hrdep = []
mindep = []
jdayrec = []
hrrec = []
minrec = []

# Confirm that the files exist in the current director and open it
if os.path.isfile(CSVfile):
	with open(CSVfile) as fid:
		lines = csv.reader(fid)
		next(lines)
		for row in lines:
			latdeg.append(row[0])
			latmin.append(row[1])
			londeg.append(row[2])
			lonmin.append(row[3])
			blanket.append(row[4])
			divenumber.append(row[5])
			deploy.append(row[6])
			jdaydep.append(row[7])
			hrdep.append(row[8])
			mindep.append(row[9])
			jdayrec.append(row[10])
			hrrec.append(row[11])
			minrec.append(row[12])		
else: 
	L = ["Unable to open file: ", CSVfile]
	print(''.join(L))
	exit()     

latdeg = np.array(latdeg, dtype='float32')
latmin = np.array(latmin, dtype='float32')
londeg = np.array(londeg, dtype='float32')
lonmin = np.array(lonmin, dtype='float32')
hrdep = np.array(hrdep, dtype='float32')
mindep = np.array(mindep, dtype='float32')
jdayrec = np.array(jdayrec, dtype='float32')
hrrec = np.array(hrrec, dtype='float32')
minrec = np.array(minrec, dtype='float32')

for i in range(0,len(deploy)):
	# Turn deployment and recovery time into date numbers
	dum1 = datetime.datetime(byr[0],1,1)+ datetime.timedelta(int(jdaydep[i]))
	mondep = dum1.strftime('%m')
	daydep = int(dum1.strftime('%d'))-1

	dum1 = datetime.datetime(byr[-1],1,1)+ datetime.timedelta(int(jdayrec[i]))
	monrec = dum1.strftime('%m')
	dayrec = int(dum1.strftime('%d'))-1

	timebase = date.toordinal(date(int(byr[0])+1,int(mondep),daydep))
	TimeDeployed = float(timebase) + (int(hrdep[i])+(int(mindep[i]))/60.0)/24.0		
	
	timebase = date.toordinal(date(int(byr[-1])+1,int(monrec),dayrec))
	TimeRecovered = float(timebase) + (int(hrrec[i])+(int(minrec[i]))/60.0)/24.0

	# Display info
	print(' ')
	L = (' Deployment number: ',deploy[i])
	J = (' Deployment time  : ',str(TimeDeployed))
	K = (' Recovery time    : ',str(TimeRecovered))
	print(''.join(L))
	print(''.join(J))
	print(''.join(K))

	# Find corresponding deployment times in *.mat file
	start = np.where(ttime >= TimeDeployed)
	end = np.where(ttime <= TimeRecovered)
	a = np.intersect1d(start,end)

	if a.size == 0:
		L = (' *************  Wrong times for deployment: ',deploy[i],'!! **************')
		print(''.join(L))
		flip = 1
	else:
		print(" Found %d records within deployment window. Extracting.." % int(a.size))
		flip = 0
		
	if i == len(deploy)-1:
		if flip == 1:
			print(' Hit exit loop in Parse data section')
			print(' Did NOT write out the golden nuggets')
			exit()

	# Output filename
	L = (str(divenumber[i]),'_',blanket[i],'_',deploy[i],'.dat')
	M = "".join(L)
	
	depmon = datetime.date(byr[0], int(mondep), 1).strftime('%b')
	recmon = datetime.date(byr[0], int(monrec), 1).strftime('%b')

	# Write out the Matlab *.mat file 
	lon = londeg[i] - (lonmin[i]/60)
	lat = latdeg[1] + (latdeg[i]/60)
	scipy.io.savemat(M, mdict={'DateTime': ttime[a],'rectimev': TimeRecovered,'deptimev': TimeDeployed,
		'Top': tdeg_corrected[a],'Bot': bdeg_corrected[a],'Longitude': lon, 'Latitude': lat})
		
	# Write the 'Golden Nugget' file
	with open(M,'w') as OutputFile:
		L = ('Creating ',M,'...')
		print(''.join(L))
		
		# Write Header
		OutputFile.write('----------------------- Begin Header ---------------------\n')
		OutputFile.write(' Blanket Letter             : %s \n' % blanket[i])
		OutputFile.write(' Blanket Deployment         : %s \n' % M[0:-4])
		OutputFile.write(' \n')
		OutputFile.write(' Bottom Thermisor ID        : %s \n' % bfilename) 
		OutputFile.write(' Bottom Thermistor Filename : %s \n' % file_bot)
		OutputFile.write(' Bottom Thermistor Offset   : %1.4f [deg C] \n' % bdeg_offset)
		OutputFile.write(' \n')
		OutputFile.write(' Top Thermistor ID          : %s \n' % tfilename) 
		OutputFile.write(' Top Thermistor Filename    : %s \n' % file_top)
		OutputFile.write(' Top Thermistor Offset      : %1.4f [deg C] \n' % tdeg_offset)
		OutputFile.write('--------------------------------------------------------\n')
		OutputFile.write(' Deployment Location Information\n')
		OutputFile.write(' Lon [deg]     : %d \n' % londeg[i])
		OutputFile.write(' Lon [dec-min] : %f \n' % lonmin[i])
		OutputFile.write(' Lat [deg]     : %d \n' % latdeg[i])
		OutputFile.write(' Lat [dec-min] : %f \n' % latmin[i])
		OutputFile.write('--------------------------------------------------------\n')
		OutputFile.write(' Deployment Time Information\n')
		OutputFile.write(' Date/Time Deployed  : %s-%s-%d %2.0f:%2.0f:00 \n' % (daydep,depmon,byr[0],int(hrdep[i]),int(mindep[i])))
		OutputFile.write(' Date/Time Recovered : %s-%s-%d %2.0f:%2.0f:00 \n' % (dayrec,recmon,byr[0],int(hrrec[i]),int(minrec[i])))
		OutputFile.write('-------------------------- End Header -------------------\n')
		OutputFile.write(' \n')
		OutputFile.write('  Date-Time              Bottom   Bottom    Bottom    Bottom    Top      Top        Top      Top\n')
		OutputFile.write('                         [raw]    [ohm]      T[C]    T(offset) [raw]    [ohm]       T[C]   T(offset)\n')

		# Write rest of Data
		for j in range(0,len(a)):
			mnhalf = datetime.date(byr[0], int(tmo[i]), 1).strftime('%b')
			OutputFile.write('%d-%s-%5d %02.0f:%02.0f:%02.0f     %5.0f  %5.4f   %1.4f   %1.4f   %5.0f  %5.4f   %1.4f   %1.4f\n' % (tdy[a[j]],
			mnhalf,tyr[a[j]],thr[a[j]],tmn[a[j]],tsec[a[j]],braw[a[j]],bres[a[j]],bdeg[a[j]],bdeg_corrected[a[j]],traw[a[j]],tres[a[j]],tdeg[a[j]],tdeg_corrected[a[j]]))
			
			
			
