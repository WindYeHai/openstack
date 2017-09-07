#-*- coding: UTF-8 -*-
import string
import os
import csv
import time
from sys import argv
import sys

def opencsv(csvfile,rowname):
        with open(csvfile,'rb') as csvfile:
                reader = csv.DictReader(csvfile)
                rowdata = [row[rowname] for row in reader]
                return rowdata

def interface_show(**kwargs):
    	lineTmpla =' '*5 + kwargs['title']+ "%-3s"
	display(lineTmpla,kwargs['minutes'],kwargs['end'])
#	print ' '*5, kwargs['title'], display(kwargs['minutes'])    	

def display(lineTmpla,mins,end):
	length = len(str(mins))-2
	sys.stdout.write(" " * length,)
	sys.stdout.flush()
        time.sleep(1)
        sys.stdout.write("\r" + lineTmpla%(mins) + end)
        sys.stdout.flush()

def linkDelay():
	filename = argv[1]
	
	Distance = opencsv(filename,'Range (km)')
	Distance = map(eval,Distance)
#	print Distance
#	Delay = [round(i/299792458*1000000,1) for i in Distance]

	Delay = [int(i/299792458*1000000) for i in Distance]
#	Delay = opencsv(filename,'Delay')
#	print Delay
#	for i in range(0,len(Distance)):
#        	distance = float(string.atof(Distance[i]))
	for i in Delay:
		os.system('tc qdisc del dev tap7cd37a48-e4 root')
		os.system('tc qdisc add dev tap7cd37a48-e4 root netem delay '+str(i)+'ms')
#		print 'delay:'+str(i)+'ms'
		interface_show(title="链路仿真延迟:",minutes=" "+str(i)+"ms",end="，按Ctrl-C退出。")
#		time.sleep(1)
	os.system('tc qdisc del dev tap7cd37a48-e4 root')
	
if __name__=='__main__':
	linkDelay()
