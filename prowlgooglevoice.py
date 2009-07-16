from googlevoicenotify import GoogleVoiceNotify
from time import sleep

class ProwlListener:
	def __init__(self):
		PROWL_API_KEY = file('prowlkey', 'r').read().strip()
		import prowlpy
		self.prowl = prowlpy.Prowl(PROWL_API_KEY)
	def on_notification(self, event, from_name, message):
		self.prowl.add('Google Voice %s' % event,from_name, message)

class PrintListener:
	def on_notification(self, event, name, message):
		print "%s: %s said %s" % (event, name, message)

if __name__ == '__main__':
	prowl_listener = ProwlListener()
	print_listener = PrintListener()
	name, passwd = file("credentials", "r").read().split()
	sleep_time = 60 
	gv = GoogleVoiceNotify(name, passwd, listeners=(prowl_listener, print_listener))
	while True:
		print "checking"
	 	gv.check()
		print "done checking, will sleep for ", sleep_time, " seconds"
		sleep(sleep_time)
