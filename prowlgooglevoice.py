from googlevoicenotify import GoogleVoiceNotify
from time import sleep

class ProwlNotify:
	def __init__(self):
		PROWL_API_KEY = file('prowlkey', 'r').read().strip()
		import prowlpy
		self.prowl = prowlpy.Prowl(PROWL_API_KEY)
	def notify(self, from_name, message):
		self.prowl.add('Google Voice',from_name, message)

if __name__ == '__main__':
	prowl_notify = ProwlNotify()
	name, passwd = file("credentials", "r").read().split()
	sleep_time = 60 
	gv = GoogleVoiceNotify(name, passwd, listeners=prowl_notify)
	while True:
		print "checking"
	 	gv.check()
		print "done checking, will sleep for ", sleep_time, " seconds"
		sleep(sleep_time)
