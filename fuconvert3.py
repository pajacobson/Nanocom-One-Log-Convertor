#!/usr/bin/env python3

#
# fuconverter.py
# author: pj@discotd5.com
# converts Nanocom One .fu1 fuel data files to .csv with all data intact.
#
#  usage:
#  python3 fuconverter.py /path/to/yourfile.fu1
#  saves .csv file to same directory as source .fu1

import csv
import sys
from os import path as Path
from struct import unpack_from

def decimal_shift(data, factor):
	return (float(data) / factor)

def k_to_c(data):
	return(float(data - 2732) / 10)

def nanoOneConvert(path):

	csvname = Path.splitext(path)[0]  + ".csv"

	with open( path, 'rb') as file:

		fdata = file.read()

		# Each "line" of log data is 64 bytes long
		# Find the number of lines by dividing the data length by line length
		# result of integer division should be an integer, but using // to be safe.

		records = len(fdata) // 64

		fuheader =  ['t', 'RPM', 'Road Speed', 'ECT', 'ECT mV', 'IAT', 'IAT mV',
			  			'Fuel Temp', 'Fuel Temp mV', 'TPS1 mV', 'TPS2 mV', 'Throttle %',
						'TPS Supply mV', 'MAP kpa', 'MAP kpa raw', 'MAF Kg/hr', 'MAF mV',
						'RPM-Idle', 'Balance 1', 'Balance 2', 'Balance 3', 'Balance 4',
						'Balance 5',  'AAP kpa', 'AAP kpa raw','EGR Inlet','WGM 1',
						'WGM 2', 'BATV1', 'BATV2']

		# If word 27:28 is same as word 29:30 log is from MSB ECU
		if (fdata[27] == fdata[29]) and (fdata[28] == fdata[30]):

			fuformat = '>xxHBHHHHxxxxHHHHHHxxHHHHhhhhhhHHHHHHH'
			k_count = 8
			dec10 = [10,12,13,22,23,24,25,26]
			maf_off = 14

		else:

			eu3 = {'AAT': 7, 'AAT mV': 8, 'TPS3 mV': 13}

			for k, v in eu3.items():
				fuheader.insert(v, k)

			fuformat = '>xxHBHHHHHHHHHHHHHHHHHhhhhhhHHHHHHH'
			k_count = 10
			dec10 = [13,15,16,25,26,27,28]
			maf_off = 17


		with open(csvname, 'w') as c:

			writer = csv.writer(c)
			writer.writerow(fuheader)

			for counter in range(records):
				updata = unpack_from(fuformat, fdata, counter * 64)

				updata = list(updata)

				for offset in range(2, k_count, 2):
					updata[offset] =  k_to_c(updata[offset])

				for offset in dec10:
					updata[offset] = decimal_shift(updata[offset], 100)

				updata[maf_off] = decimal_shift(updata[maf_off], 10)

				updata.insert(0,counter)
				writer.writerow(updata)


if __name__ == '__main__':

	nanoOneConvert(sys.argv[1])
