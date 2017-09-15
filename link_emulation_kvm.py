#!/usr/bin/env python
#-*- coding=utf-8 -*-

import bottle
import re
import os
import libvirt
import json

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = '7777'
RE_MAC_ADDRESS = re.compile(r'^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$')

app=bottle.Bottle()

res={'result':'','info':''}

def validate_mac(mac):
	return RE_MAC_ADDRESS.match(mac)
	
def run(host=None,port=None):
	host=host or DEFAULT_HOST
	port=port or DEFAULT_PORT
	return app.run(host=host,port=port)

def resultInfo(res):
	return json.dumps(res)
	
@app.route('/v3.0/link_emulation_kvm',method='POST')
def setLink():
	instance_name=bottle.request.POST.get('instance_name')
	mac=bottle.request.POST.get('mac')
	average=int(bottle.request.POST.get('bandwidth'))
	#peak=int(bottle.request.POST.get('peak'))
#	delay=int(bottle.request.POST.get('delay'))
        delay=bottle.request.POST.get('delay')
	loss=int(bottle.request.POST.get('loss'))
	print instance_name,mac,average,delay,loss
	if not validate_mac(mac):
		res['result']=0
		res['info']='invalid mac'
		return resultInfo(res)+"\n"
		#return 'result:0 errInfo:invalid mac\n'
	b_res=setBandwidth(instance_name,mac,average)
	d_res=setDelayAndLoss(instance_name,mac,delay,loss)
        print average,b_res,d_res
	if average==0 and b_res==0 and d_res==0:
		res['result']=1
		if delay==0 and loss==0:
			res['info']='clear bandwidth,delay and loss successful'
		elif delay!=0 and loss==0:
			res['info']='set delay successful'
                elif delay==0 and loss!=0:
                        res['info']='set loss successful'
                elif delay!=0 and loss!=0:
                        res['info']='set delay and loss successful'
	elif average!=0 and b_res==0 and d_res==0:
		res['result']=1
		if delay==0 and loss==0:
			res['info']='set bandwidth successful'
		elif delay!=0 and loss==0:
			res['info']='set bandwidth and delay successful'
                elif delay==0 and loss!=0:
		        res['info']='set bandwidth and loss successful'
		else:
		        res['info']='set bandwidth,delay and loss successful'
	return resultInfo(res)+"\n"

def getVport(instance_name,mac):
	conn=libvirt.open(None)
	dom=conn.lookupByName(instance_name)
	xml=dom.XMLDesc()
	macIndex=xml.find(mac)
	if macIndex==-1:
		res['result']=0
		res['info']='mac does not exist'
		resultInfo(res)
		#return 'result:0 errInfo:mac does not exist'
	vport=xml[xml.find('tap',macIndex):xml.find('tap',macIndex)+14]
	print vport
	conn.close()
	return vport
	
def setBandwidth(instance_name,mac,average):
	params={'inbound.average':average,
			'inbound.burst':0,
			'inbound.peak':0,
			'outbound.average':average,
			'outbound.burst':0,
			'outbound.peak':0
			}
	flag=-1
	conn=libvirt.open(None)
	try:
		dom=conn.lookupByName(instance_name)
		#xml=dom.XMLDesc()
		#vport=xml[xml.find('tap'):xml.find('tap')+14]
		vport=getVport(instance_name,mac)
		#vport='vnet0'
		#print dom.interfaceParameters(vport,1)
		flag=dom.setInterfaceParameters(vport,params,1)
		#dom.setInterfaceParameters(vport,params,2)
		#print dom.interfaceParameters(vport,1)
		#print dom.interfaceParameters(vport,2)
	except libvirt.libvirtError as e:
		res['result']=0
		res['info']='instance name does not exist'
		resultInfo(res)
	finally:
		conn.close()
	return flag
	
def setDelayAndLoss(instance_name,mac,delay,loss):
	vport=getVport(instance_name,mac)
	#vport='vnet0'
	flag=-1
	#if delay==0 and loss==0:
	#flag=0
	f=os.popen('tc qdisc ls dev '+vport)
	data=f.readline()
	#print data
	#f.close()
	if data.find('htb')!=-1:
           #print 'htb'
	   os.system('tc qdisc del dev '+vport+' parent 1:1 handle 2: sfq perturb 10')
	   if delay!=0 and loss!=0:
	      flag=os.system('tc qdisc add dev '+vport+' parent 1:1 handle 2: netem delay '+str(delay)+'ms loss '+str(loss)+'%')
	   elif delay!=0 and loss==0:
	      flag=os.system('tc qdisc add dev '+vport+' parent 1:1 handle 2: netem delay '+str(delay)+'ms')
	   elif delay==0 and loss!=0:
	      flag=os.system('tc qdisc add dev '+vport+' parent 1:1 handle 2: netem loss '+str(loss)+'%')
           else:
              data=f.readline()
              if data.find('netem')!=-1:
                 flag=os.system('tc qdisc del dev '+vport+' parent 1:1 handle 2:')
	      flag=0

	elif data.find('netem')!=-1:
                #print 'netem'
		os.system('tc qdisc del dev '+vport+' root')
        #if delay==0 and loss==0:
		#os.system('tc qdisc del dev '+vport+' root')
		#flag=0
		if delay!=0 and loss!=0:
		    flag=os.system('tc qdisc add dev '+vport+' root netem delay '+str(delay)+'ms loss '+str(loss)+'%')
		elif delay!=0 and loss==0:
		    flag=os.system('tc qdisc add dev '+vport+' root netem delay '+str(delay)+'ms')
                elif delay==0 and loss!=0:
		    flag=os.system('tc qdisc add dev '+vport+' root netem loss '+str(loss)+'%')
		#if flag!=0:
			#os.system('tc qdisc del dev '+vport+' root')
			#flag=os.system('tc qdisc add dev '+vport+' root netem delay '+str(delay)+'s')
        else:
             if delay!=0 and loss==0:
                flag=os.system('tc qdisc add dev '+vport+' root netem delay '+str(delay)+'ms')
             elif delay==0 and loss!=0:
                flag=os.system('tc qdisc add dev '+vport+' root netem loss '+str(loss)+'%')
             elif delay!=0 and loss!=0:
                flag=os.system('tc qdisc add dev '+vport+' root netem delay '+str(delay)+'ms loss '+str(loss)+'%')    
             else:
                flag=0
	f.close()
        return flag
			
if __name__=='__main__':
	run('0.0.0.0','7777')
