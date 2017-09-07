#!/usr/bin/env python
# -*- coding:utf-8 -*-
import paramiko
import os
import re
import csv
from sys import argv

def opencsv(csvfile,rowname):
        with open(csvfile,'rb') as csvfile:
                reader = csv.DictReader(csvfile)
                rowdata = [row[rowname] for row in reader]
                return rowdata
 
#误码率仿真量级为10^-3~10^-6
def bertrans():
#	listsend = [1.5*pow(10,-6),4.3*pow(10,-5),2.9*pow(10,-4),9.1*pow(10,-3)]
	filename = argv[1]
	listsend = opencsv(filename,'BER')
	for i in listsend:
               	bernum = float(i)*pow(10,6)
               	packetlossmin = (bernum/(1460*8)+1)/85*100
#		print 'min:',packetlossmin
		packetlossmax = min(bernum,85)/85*100
#		print 'max:',packetlossmax
		packetlossavg = (packetlossmin + packetlossmax)/2
#		print 'avg:',packetlossavg
#		print 'pklavg:',packetlossavg,'%'
		os.system('tc qdisc del dev tap7cd37a48-e4 root')
		os.system('tc qdisc add dev tap7cd37a48-e4 root netem loss '+str(packetlossavg)+'%')
		res = Remotessh()
		print 'BER:'+str(i)+' '+res+'  Hit Ctrl-C to quit simulation'
	os.system('tc qdisc del dev tap7cd37a48-e4 root')

def Remotessh():
	#创建ssh对象
	ssh = paramiko.SSHClient()
	#允许连接不在know_host中的主机
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	#连接服务器
	ssh.connect(hostname='192.168.1.21',port=22,username='root',password='jnopenstack')
	#执行命令
	stdin, stdout, stderr = ssh.exec_command('ip netns exec qdhcp-cac6f458-a9c5-44d9-a859-f0e3c279c313 sshpass -p ubuntu ssh 192.168.22.6 python ScapySend.py')
	#执行结果 result = stderr.read() #如果有错误则打印
#	print stderr
	result = stdout.read()
	res = re.findall(r"\d+\.\d% hits",result)
	#关闭连接
	ssh.close()
	return res[0]

if __name__=='__main__':
	bertrans()
