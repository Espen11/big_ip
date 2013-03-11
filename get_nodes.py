#!/bin/env python

import sys, os
import pycontrol.pycontrol as pc
import getpass
from optparse import OptionParser


def list_lb(server,user,password):
	b = pc.BIGIP(
	        hostname = server,
	        username = user,
	        password = password,
	        fromurl = True,
	        wsdls = ['LocalLB.Pool','LocalLB.VirtualServer','LocalLB.PoolMember'])
	
	vips = b.LocalLB.VirtualServer.get_list()
	csv = []
	for vip in vips:
		print vip
		line = '%s,' % server
		line += '%s' %vip
	
		vip_info = b.LocalLB.VirtualServer.get_destination([vip])
		vip_ip = vip_info[0][0]
		vip_port = vip_info[0][1]
		line += ',%s:%s' %(vip_ip,vip_port)
	
		pool = b.LocalLB.VirtualServer.get_default_pool_name([vip])
		line += ',%s' %pool[0]
	
		line += ','
		members = b.LocalLB.Pool.get_member([pool])
		for member in members:
			for values in member:
				ip = values[0]
				port = values[1]
				line += '%s:%s;' %(ip,port)
				print "\t%s:%s" %(ip,port)
#		print '%s\n' % line
		csv.append(line)
	return csv

def write_csv(csv):
	print '\nWriting to csv:'
	f = open('lb.csv','w')
	for line in csv:
		f.write('%s\n'%line)
	
	f.close()

def start(servers):
	user = 'admin'
	print 'Login with %s, type in the password:' % user
	password = getpass.getpass()

	csv = []
	arr = servers.split(',')
	for server in arr:
		list = list_lb(server,user,password)
		for line in list:
		 	csv.append(line)
	write_csv(csv)
	return

####################################################

if __name__ == '__main__':
	usage = "Usage: %prog [options]"
	parser = OptionParser(usage=usage)
	parser.add_option('-s', '--server', dest='server', help='hostname of the big-ip', metavar='hostname')
#	parser.add_option('-c', '--csv', dest='cvs', help='write to csv', action="store_true")

	(options, args) = parser.parse_args()


	if options.server:
		start(options.server)
