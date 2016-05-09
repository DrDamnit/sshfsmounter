#!/usr/bin/python
import os, sys, shutil, string
import readline
import getpass
import re
import logging
import ConfigParser

def sizeof_fmt(num, suffix='B'):
	for unit in ['','K','M','G','T','P','E','Z']:
		if abs(num) < 1024.0:
			return "%3.1f%s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.1f%s%s" % (num, 'Yi', suffix)

class smounter(object):

	PROMPT="SSHFS Mount> "
	LOGIC = ""


	def __init__(self):

		if not getpass.getuser() == 'root':
			sys.exit("You must run this script as root. Quitting.")

		readline.set_completer(self.complete)
		readline.parse_and_bind("tab: complete")

		# Setup the data file where we are going to store all our connections.
		datafile = os.path.expanduser("~/.smount")

		# If it doesn't exist, "touch" it.
		if not os.path.exists(datafile):
			fhandle = open(datafile, 'a')
			try:
				os.utime(datafile, None)
			finally:
				fhandle.close()

		#Save it into a class var so we can access it later.
		self.datafile = datafile

		# Load configs.
		self.config = ConfigParser.RawConfigParser()
		self.config.read('/etc/smount.conf')

		self.loadSites()
		try:
			print "SSHFS Home Directory: " , self.config.get('smount', 'home')
			pass
		except Exception, e:
			print "WARNING: No home directory setting defined in /etc/smount.conf. Use set config home to save home directory."
		print "System Loaded. Ready."


	def traverse(self,tokens,tree):
		if tree is None:
			return []
		elif len(tokens) == 0:
			return []

		if len(tokens) == 1:
			return [x+' ' for x in tree if x.startswith(tokens[0])]
		else:
			if tokens[0] in tree.keys():
				return self.traverse(tokens[1:],tree[tokens[0]])
			else:
				return []
		return []

	def complete(self, text, state):
		try:
			tokens = readline.get_line_buffer().split()
			if not tokens or readline.get_line_buffer()[-1] == ' ':
				tokens.append(text)
			results = self.traverse(tokens,self.LOGIC) + [None]
			return results[state]
		except Exception,e:
			print e

	def dispVersion(self):
		print "SSHFS Mounter - Manage SSHFS Mount Points and Credentials."
		print ""
		print "Copyright (c) 2016 High Powered Help, Inc. All Rights Reserved."
		print "This program is free software: you can redistribute it and/or modify"
		print "it under the terms of the GNU General Public License as published by"
		print "the Free Software Foundation, either version 3 of the License, or"
		print "(at your option) any later version."
		print ""
		print "This program is distributed in the hope that it will be useful,"
		print "but WITHOUT ANY WARRANTY; without even the implied warranty of"
		print "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
		print "GNU General Public License for more details."
		print ""
		print "You should have received a copy of the GNU General Public License"
		print "along with this program.  If not, see <http://www.gnu.org/licenses/>.		"

	def parseSites(self):
		f = open(self.datafile,'r')
		buffer = f.readlines()
		f.close

		sites = []
		for line in buffer:
			x = line.split("|")
			sites.append(x[0])

		d = dict((s,None) for s in sites)

		return d

	def loadSites(self):



		self.LOGIC = {
		'createmount': None,
		'mount': self.parseSites(),
		'config':
		{
			'set':{
				'home':None
			},
		},
		'sites':
		{
			'show':None,
			'reload':None
		},
		'unmount':
		{
			'all':None
		},
		'version':
		{},
		'exit':
		{}
	}

	def saveSite(self,name,user,uri,rdir):
		site = (name,user,uri,rdir)
		line = "|".join(site)+"\n"
		f = open(self.datafile,'a')
		f.write(line)
		f.close
		print "Site Saved"

	def getSite(self,name):
		f = open(self.datafile,'r')
		buffer = f.readlines()
		f.close

		for x in buffer:
			y = x.split("|")
			if(y[0]==name):
				return (y[1],y[2],y[3].strip())
		return False

	def showSites(self):
		f = open(self.datafile,'r')
		buffer = f.readlines()
		f.close

		row = ['Name','User','URI','Directory']
		print "".join(str.ljust(i,20) for i in row)

		for x in buffer:
			y = x.split("|")
			print "".join(str.ljust(i.strip(),20) for i in y)

	def setHome(self,dir):
		if not os.path.isdir(dir):
			try:
				os.makedirs(dir)
			except Exception, e:
				print "Home directory does not exist, or I couldn't create it. Command failed."
				return False
		# self.config = ConfigParser.RawConfigParser()
		if not self.config.has_section('smount'):
			self.config.add_section('smount')

		self.config.set('smount','home',dir)
		# Writing our configuration file to '/etc/smount.conf'
		with open('/etc/smount.conf', 'wb') as configfile:
			self.config.write(configfile)
		print "Home directory saved as: " , self.config.get('smount','home')

	def createMount(self):
		name=raw_input("Name this entry: ")
		user=raw_input("Enter the username for the remote server: ")
		addr=raw_input("Enter the address of the remote server: ")
		rdir=raw_input("Enter the remote directory to mount: ")

		self.saveSite(name,user,addr,rdir)
		self.loadSites()

	def mount(self,name):
		result = self.getSite(name)
		if(result) == False:
			print "Site unknown. #fail"
			return False

		user,uri,path = result
		resourceString = "%s@%s:%s" % (user,uri,path)
		localPath = os.path.join(self.config.get('smount','home'),name)

		if not os.path.isdir(localPath):
			os.makedirs(localPath)

		cmd = "sshfs -oallow_other %s %s" % (resourceString,localPath)
		print "Running: %s"%cmd
		os.system(cmd)

	def unmount(self,name):
		root=self.config.get('smount','home')
		if(name=='all'):
			print "Unmounting everything"
			for d in os.listdir(root):
				cmd = "fusermount -u %s" % os.path.join(root,d)
				print "Running: %s" %cmd
				os.system(cmd)
			print "Done."
		else:
			if os.path.isdir(os.path.join(root,name)):
				cmd = "fusermount -u %s" % os.path.join(root,name)
				print "Running: %s" %cmd
				os.system(cmd)
			else:
				print "This directory does not exist. #fail"

	def start(self):
		while True:
			cmd = raw_input(self.PROMPT)
			cmd = cmd.strip()
			if cmd == "help":
				self.dispVersion()
			elif cmd.startswith('unmount'):
				tokens = cmd.split()
				self.unmount(tokens[1])
			elif cmd.startswith('mount'):
				tokens = cmd.split()
				self.mount(tokens[1])
			elif cmd == 'createmount':
				self.createMount()
			elif cmd == 'sites reload':
				self.loadSites()
				print 'Sites reloaded. Check with command "sites show"'
			elif cmd == 'sites show':
				self.showSites()
			elif cmd == 'show config':
				print "Showing configuration for smount (/etc/smount.conf)"
				for name,value in self.config.items('smount'):
					print "%s: %s" % (name,value)
			elif cmd.startswith('config set home'):
				tokens = cmd.split(" ")
				dir = ''
				try:
					dir = tokens[3]
					pass
				except Exception, e:
					print "You did not specify a home directory. #fail"
					continue
				self.setHome(dir)
			elif cmd == "exit" or cmd == "quit":
				return True
			else:
				print "Command not recognized."

s = smounter()
s.start()
