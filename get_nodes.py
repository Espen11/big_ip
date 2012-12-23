#!/bin/env python

import sys, os
import pycontrol.pycontrol as pc
import getpass
from optparse import OptionParser


def list_lb(server):
	user = 'admin'
	print 'Login to %s:%s, type in the password:' % (user,server)
	password = getpass.getpass()
	b = pc.BIGIP(
	        hostname = server,
	        username = user,
	        password = password,
	        fromurl = True,
	        wsdls = ['LocalLB.Pool','LocalLB.VirtualServer','LocalLB.PoolMember'])
	
	vips = b.LocalLB.VirtualServer.get_list()
	print 'format:\nvip => vip-ip:port\n\tpool\n\t\tmembers-ip:port\n'
	print 'csv format:\nvip-name, vip-ip:port, pool-name, member-ip:port, member-ip:port, ...etc\n\n'
	csv = []
	for vip in vips:
		line = ''
		sys.stdout.write('%s => ' % vip)
		line += '%s' %vip
	
		vip_info = b.LocalLB.VirtualServer.get_destination([vip])
		vip_ip = vip_info[0][0]
		vip_port = vip_info[0][1]
		print '%s:%s'%(vip_ip,vip_port)
		line += ',%s:%s' %(vip_ip,vip_port)
	
		pool = b.LocalLB.VirtualServer.get_default_pool_name([vip])
		print '\t%s'%pool[0]
		line += ',%s' %pool[0]
	
		members = b.LocalLB.Pool.get_member([pool])
		for member in members:
			for values in member:
				ip = values[0]
				port = values[1]
				print '\t\t%s:%s' % (ip,port)
				line += ',%s:%s' %(ip,port)
		csv.append(line)
		print ''
	return csv
	
def write_cvs(csv):
	print '\nWriting to csv:'
	f = open('lb.csv','w')
	for line in csv:
		f.write('%s\n'%line)
	
	f.close()

####################################################

server = 'lb2.infra.eniro'
#server = 'load1.findexa.net'

if __name__ == '__main__':
	usage = "Usage: %prog [options]"
	parser = OptionParser(usage=usage)
	parser.add_option('-s', '--server', dest='server', help='hostname of the big-ip', metavar='hostname')
	parser.add_option('-c', '--cvs', dest='cvs', help='write to cvs', action="store_true")

	(options, args) = parser.parse_args()


	if options.server:
		cvs = list_lb(options.server)
		if options.cvs:
			write_cvs(cvs)
