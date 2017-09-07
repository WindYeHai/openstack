#-*- coding: UTF-8 -*-
import csv
import time
from sys import argv
import sys
import os

def opencsv(csvfile,rowname):
	with open(csvfile,'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		rowdata = [row[rowname] for row in reader] 
		return rowdata

def interface_show(**kwargs):
#    	lineTmpla = ' '*5 + kwargs['title'] + " %-3s"
	Access = ' '*5 + kwargs['access']
	lineTmpla = kwargs['title'] + "%s" 
   	lineTmpla1 = kwargs['end']
    	time_remain(Access,lineTmpla,kwargs['minutes'],lineTmpla1)

def time_remain(access,lineTmpla,mins,lineTmpla1):
    	count = 0
    	while (count < mins):
        	count += 1
        	n = mins - count
        	time.sleep(1)
        	sys.stdout.write("\r" + access + lineTmpla %(n) + lineTmpla1)
        	sys.stdout.flush()
#        	if not n:
#			sys.stdout.write(("\r" + " "*50)
#			sys.stdout.write("\r" + "链路已断开")
#			sys.stdout.flush()
#			return 'completed'

def linkAccess():
	flag = 0
	flag1 = 0
	filename = argv[1]
	if filename == "":
		print "文件名不能为空"
	StartTime = opencsv(filename,'Start Time (UTCG)')
	StopTime = opencsv(filename,'Stop Time (UTCG)')
	num = opencsv(filename,'Access')
	for i in range(0,len(StartTime)):
		starttime = StartTime[i]
		stoptime = StopTime[i]
		starttime = time.mktime(time.strptime(starttime,'%d %b %Y %H:%M:%S'))
		stoptime = time.mktime(time.strptime(stoptime,'%d %b %Y %H:%M:%S'))
		flag = flag+1
		result = '正处于第'+str(flag)+'可见时段内'
		result1 = '正处于第'+str(flag-1)+','+str(flag)+'可见时段之间'
		t = 0
		a = 0
		b = 0
		if (flag == len(num)) and (time.time() > starttime) and (time.time() > stoptime):
			print ' '*5 + "该链路此周期内不可通"
			os.system('tc qdisc add dev tap7cd37a48-e4 root netem delay 30s')
			break
		if (time.time() > starttime) and (time.time() > stoptime):
			continue
		while t<2: 
			if(starttime <= time.time()) and (stoptime >= time.time()):
				os.system('tc qdisc del dev tap7cd37a48-e4 root')
				while(starttime <= time.time()) and (stoptime >= time.time()):
#				print '目前该链路已通',int(stoptime-time.time()),'s后链路断开'
					interface_show(access=result,title=",链路状态为通,",minutes=int(stoptime-time.time()),end="s后链路断开")		
					time.sleep(1)
					
				a = a + 1
#				if(stoptime < time.time()):
#					print '目前链路已断开'
#					break	

			elif(starttime > time.time()) or (stoptime < time.time()):
			
				os.system('tc qdisc add dev tap7cd37a48-e4 root netem delay 30s')
				
				while(starttime > time.time() or stoptime < time.time()) :
					interface_show(access=result1,title=",链路断开,",minutes=int(starttime-time.time()),end="s后链路可通")				
					time.sleep(1)
				b = b + 1
				if a==1 and b==1:
					continue
				if a==1 and b==2:
					continue
				
			t = t + 1
#	print flag1	
#	return flag,num,flag1
	
if __name__=='__main__':
	linkAccess()
#	flag,num,flag1 = linkAccess()
#	print flag,len(num)
#	if (flag == len(num)) and (flag1 == 0):
#		print ' i'*5 + "该链路此周期内不可通"		
