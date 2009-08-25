from googlevoicenotify import GoogleVoiceNotify
from time import sleep
from os import environ, path
import sys
from getpass import getpass

class ProwlListener:
	def __init__(self,prowlkey = environ['HOME']+'/.prowlapi'):
		if not path.exists(prowlkey):
			# fallback to prowlkey in the same folder
			prowlkey = 'prowlkey'
		PROWL_API_KEY = file(prowlkey, 'r').read().strip()
		import prowlpy
		self.prowl = prowlpy.Prowl(PROWL_API_KEY)
	def on_notification(self, event, from_name, message):
		self.prowl.add('%s' % event,from_name, message)

class PrintListener:
	def on_notification(self, event, name, message):
		print "%s: %s said %s" % (event, name, message)

def readparams(cfile):
	params = dict()
	try:
		for ln in open(cfile).readlines():
			if not ln[0] in ('#',';'):
				key,val = ln.strip().split('=',1)
				params[key.lower()] = val
	except:
		print 'cfile not read.'
	try:
		params['gvid']
	except:
		params['gvid'] = raw_input('Google login: ')
	try:
		params['password']
	except:
		params['password'] = getpass('%s password: '%params['gvid'])
	try:
		params['sleep']
	except:
		params['sleep'] = 60
	return params['sleep'], params['gvid'], params['password']

if __name__ == '__main__':
	try:
		prowl_listener = ProwlListener()
		print_listener = PrintListener()
	except Exception, e:
		print e
		print 'Could not load ProwlListener...exiting.'
		sys.exit()
	cfile = environ['HOME']+'/.gvnotify'
	try:
		sleep_time, name, passwd = readparams(cfile)
	except:
		print 'Could not load Google Voice info...exiting.'
		sys.exit()
	gv = GoogleVoiceNotify(name, passwd,
		listeners=(prowl_listener, print_listener),
		picklefile = environ['HOME']+'/.gvcache')
	del passwd
	while True:
		# uncomment below for debugging
		# print 'sleeping...'
		gv.check()
		sleep(sleep_time)

