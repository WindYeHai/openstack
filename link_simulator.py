#!/usr/bin/env python
#-*- coding: UTF-8 -*-
import csv
import time
import sys
import os
import paramiko
import bottle
import libvirt
import json
import gevent
from gevent import monkey; monkey.patch_all()
import re

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '6666'
DEFAULT_SERVER = 'gevent'
RE_MAC_ADDRESS = re.compile(r'^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')
app=bottle.Bottle()

#res={'result':'','info':''}
res={'info':'','result':''}
res1={'Connection':'','Period':'','delay':'','ber':'','Time left':''}


def validate_mac(mac):
	return RE_MAC_ADDRESS.match(mac)

def run(host=None,port=None,server=None):
	host=host or DEFAULT_HOST
	port=port or DEFAULT_PORT
	server=server or DEFAULT_SERVER
	return app.run(host=host,port=port,server=server)

def resultInfo(res):
	return json.dumps(res,sort_keys=True)

@app.route('/v2.0/test',method='POST')
def setLink():
	res['result']=1
	instance_name=bottle.request.POST.get('instance_name')
	mac=bottle.request.POST.get('mac')
	filename=bottle.request.POST.get('filename')	
	ip=bottle.request.POST.get('ip')
	pyfile=bottle.request.POST.get('pyfile')
	if not validate_mac(mac):
		res['result']=0
		res['info']='invalid mac'
	vport=getVport(instance_name,mac)
	print instance_name,mac,vport,filename,ip,pyfile
	print "The simulation is in progress......................."
	m=linkAccess(instance_name,mac,filename,ip,pyfile)
#	for i in m:
#		print res1
#		yield resultInfo(res1)+"\n"
#		time.sleep(2)

	if res['result']==0:
		yield resultInfo(res)+"\n"
	else:
		for i in m:
			yield resultInfo(res1)+"\n"

def getVport(instance_name,mac):
	conn=libvirt.open(None)
	dom=conn.lookupByName(instance_name)
	xml=dom.XMLDesc()
	macIndex=xml.find(mac)
	if macIndex==-1:
		res['result']=0
		res['info']='mac does not exist'
		resultInfo(res)
	vport=xml[xml.find('tap',macIndex):xml.find('tap',macIndex)+14]
#	print vport
	conn.close()
	return vport

def opencsv(csvfile,rowname):
	with open(csvfile,'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		rowdata = [row[rowname] for row in reader] 
		return rowdata

def interface_show(**kwargs):
	flag=kwargs['flag']

#	Access = ' '*5 + kwargs['access']
#	lineTmpla = kwargs['title'] + "%s" 
#  	lineTmpla1 = kwargs['end']

	delay = kwargs['delay']
	ber = kwargs['ber']
	vport = kwargs['vport']
	mins = kwargs['minutes']
	ip = kwargs['ip']
	pyfile = kwargs['pyfile']
#	print 0
	if delay=="" and ber=="":
		count=0
		while(count<mins):
			count+=1
			n=mins-count
			time.sleep(1)
#			sys.stdout.write("\r" + Access + lineTmpla %(n) + lineTmpla1)
#                	sys.stdout.flush()
	
			res1['Connection']="off"
			res1['Period']=str(flag-1)+"~"+str(flag)
			res1['delay']="none"
			res1['ber']='none'
			res1['Time left']=str(n)+"s"
#			print resultInfo(res1)
			yield res1		

			if not n:
				return
	else:    
           	count=0
#		print delay,ber
               	pacloss=bertrans(ber)
#		print "count",count
               	while (count<mins):
                       	if count % 60 == 0:
                               	num = count/60
   	                       	os.system('tc qdisc del dev '+vport+' root')
                               	os.system('tc qdisc add dev '+vport+' root netem delay '+str(delay[num])+'ms loss '+str(pacloss[num])+'%')
                               
				Remotessh(ip,pyfile)
			
                       	count += 1
                       	n = mins - count
                       	time.sleep(1)
                       	if n==0 and num==len(delay)-2:
                               	num += 1
#                       sys.stdout.write("\r" + Access + lineTmpla %(n) + lineTmpla1 +",此时链路延时为"+str(delay[num])+"ms"+",链路误码率为"+str(ber[num])+" ")
#                       sys.stdout.flush()
		   	
#			print "delay,ber:",delay[num],ber[num]
		       	
			res1['Connection']="on"
		       	res1['Period']=str(flag)
                       	res1['delay']=str(delay[num])+"ms"
                       	res1['ber']=str(ber[num])
                       	res1['Time left']=str(n)+"s"
		       	yield res1

                       	if not n:
                              	return 

def linkDelayAndBer(starttime,stoptime,filename):
	Time = opencsv(filename,'Time (UTCG)')
	Distance = opencsv(filename,'Range (km)')
        Distance = map(eval,Distance)
	BER = opencsv(filename,'BER')
	Time1=[]
	distance=[]
	ber=[]
	time1=[]
	for t in range(0,len(Time)):
		Time1.append(time.mktime(time.strptime(Time[t],'%d %b %Y %H:%M:%S')))
	for i in range(0,len(Time1)):
		if Time1[i]>=starttime and Time1[i]<=stoptime:
#			print Time1[i]
			distance.append(Distance[i])	
			ber.append(BER[i])
			time1.append(Time1[i])
#	print time.time(),time1[0]
	t = time1[0]-time.time()
#	print t,int(t)
	if int(t) <=55:
		time.sleep(int(t))
	Delay = [int(s/299792458*1000000) for s in distance]
	return Delay,ber

#误码率仿真量级为10^-3~10^-6
def bertrans(bersend):
	pacloss=[]
	for i in bersend:
		bernum = float(i)*pow(10,6)
        	packetlossmin = (bernum/(1460*8)+1)/85*100
       		packetlossmax = min(bernum,85)/85*100
        	packetlossavg = (packetlossmin + packetlossmax)/2
		pacloss.append(packetlossavg)
	return pacloss

def Remotessh(ip,pyfile):
        #创建ssh对象
        ssh = paramiko.SSHClient()
        #允许连接不在know_host中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh.connect(hostname='192.168.1.21',port=22,username='root',password='jnopenstack')
        #执行命令
        stdin, stdout, stderr = ssh.exec_command('ip netns exec qdhcp-cac6f458-a9c5-44d9-a859-f0e3c279c313 sshpass -p ubuntu ssh '+str(ip)+' python '+str(pyfile))
        #执行结果 result = stderr.read() #如果有错误则打印
        ssh.close()

def StartAndStop(filename):
        Time = opencsv(filename,'Time (UTCG)')
        Time1=[]
        flag=[]
        for t in range(0,len(Time)):
                Time1.append(time.mktime(time.strptime(Time[t],'%d %b %Y %H:%M:%S')))
        s=1
        for t in range(1,len(Time1)):
                if Time1[t]-Time1[t-1]<=60:
                        flag.append(s)
                else:
                        flag.append(s)
                        s=s+1
        flag.append(s)
        num=max(flag)
        a=0
        b=[]
        c=0
        Starttime=[]
        Stoptime=[]
        for i in range(1,num+1):
                num1=0
                for j in flag:
                        if j==i:
                                num1=num1+1
                a=a+num1
                b.append(a)
        for i in b:
                if i==min(b):
                        Starttime.append(Time[0]),Stoptime.append(Time[i-1])
                else:
                        Starttime.append(Time[b[c-1]]),Stoptime.append(Time[i-1])
                c=c+1
#        print Starttime,Stoptime
        return Starttime,Stoptime


def linkAccess(instance_name,mac,filename,ip,pyfile):
	vport = getVport(instance_name,mac)
	flag = 0

	StartTime,StopTime = StartAndStop(filename)

#	StartTime = opencsv(accessfilename,'Start Time (UTCG)')
#	StopTime = opencsv(accessfilename,'Stop Time (UTCG)')
	num = len(StartTime)
	for i in range(0,num):
		starttime = StartTime[i]
		stoptime = StopTime[i]
		starttime = time.mktime(time.strptime(starttime,'%d %b %Y %H:%M:%S'))
		stoptime = time.mktime(time.strptime(stoptime,'%d %b %Y %H:%M:%S'))
		flag = flag+1
		result = '正处于第'+str(flag)+'可见时段内'
		result1 = '正处于第'+str(flag-1)+','+str(flag)+'可见时段之间'
		times = 0
		a = 0
		b = 0
		if (flag == num) and (time.time() > starttime) and (time.time() > stoptime):
			print ' '*5 + "该链路周期内已不再可通"
			os.system('tc qdisc del dev '+vport+' root')
			os.system('tc qdisc add dev '+vport+' root netem delay 30s')
			res1['Connection']=0
			res1['Period']='none'
			res1['Time left']='none'
			res1['delay']='none'
			res1['ber']='none'
			yield resultInfo(res1)
			
		if (time.time() > starttime) and (time.time() > stoptime):
			continue
		while times<2: 
			if(starttime <= time.time()) and (stoptime >= time.time()):				
				while(starttime <= time.time()) and (stoptime >= time.time()):
					delay,ber=linkDelayAndBer(time.time(),stoptime,filename)
#					print delay,ber
#					t=interface_show(flag=flag,access=result,title=",链路状态为通,",minutes=int(stoptime-time.time()),end="s后链路断开",delay=delay,ber=ber,vport=vport)                                     
					t=interface_show(flag=flag,minutes=int(stoptime-time.time()),delay=delay,ber=ber,ip=ip,pyfile=pyfile,vport=vport)
					for i in t:
#                                               yield resultInfo(res1)+"\n"
#						print res1
                                                yield res1
					
#					interface_show(flag=flag,minutes=int(stoptime-time.time()),delay=delay,ber=ber,vport=vport)
				a+=1

			elif(starttime > time.time()) or (stoptime < time.time()):
				os.system('tc qdisc del dev '+vport+' root')
				os.system('tc qdisc add dev '+vport+' root netem delay 30s')				
				while(starttime > time.time()) or (stoptime < time.time()):
#					t=interface_show(flag=flag,access=result1,title=",链路断开,",minutes=int(starttime-time.time()),end="s后链路可通",delay="",ber="",vport=vport)
					t=interface_show(flag=flag,minutes=int(starttime-time.time()),delay="",ber="",ip=ip,pyfile=pyfile,vport=vport)
					for i in t:
#						yield resultInfo(res1)+"\n"
#						print res1
						yield res1
						
				b+=1
				if (a==1 and b==1) or (a==1 and b==2):
					continue		
			times = times + 1	

if __name__=='__main__':
	run('0.0.0.0','6666','gevent')
