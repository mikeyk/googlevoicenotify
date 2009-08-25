"""

Google Voice Notify, v0.1
by Mike Krieger <mikekrieger@gmail.com>

"""

from cookielib import CookieJar
import simplejson
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import urllib2
import cPickle as pickle
from httplib import IncompleteRead

class GoogleVoiceNotify(object):
	def __init__(self, username, password, listeners=None, picklefile='/tmp/pickled-updates'):
		"""
		Initialize the Google Voice Notifier 
		"""
		# GV username and pass
		self.username = username
		self.password = password
		self.picklefile = picklefile	
		self.headers = [("Content-type", "application/x-www-form-urlencoded"),
														('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'),
														("Accept", "application/xml")]
		# only fetch cookies once
		self.cookies = CookieJar()
		# if a previous session quit but saved state, load it to
		# avoid double notifications
		try:
			cached_fl = open(picklefile, 'r')
			self.convo_threads = pickle.load(cached_fl)
			cached_fl.close()
		except Exception, e:
			from collections import defaultdict
			self.convo_threads = defaultdict(set)
		"""
			Register a list of listeners that print out notifications.
			Listeners must implement an 'on_notification' method,
			of the format on_notification(event, from_name, message)
		"""
		if type(listeners) in (tuple, list):
			self.listeners = listeners
		elif listeners != None:
			self.listeners = (listeners,)
		else:
			self.listeners = None

	def do_req(self, url, post_data=None):
		# reference: http://media.juiceanalytics.com/downloads/pyGAPI.py
		req = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
		if post_data is not None:
			req.add_data(post_data)
		req.addheaders = self.headers
		f = req.open(url)
		return f

	def get_inbox(self):
		# if we haven't acquired cookies yet
		if len(self.cookies) == 0:
			 # first do the login POST
			login = self.do_req('https://www.google.com/accounts/ServiceLoginBoxAuth?Email=%s&Passwd=%s&service=grandcentral' % (self.username, self.password)).read()
			 # second step is to pass the cookie check
			cookie_check = self.do_req('https://www.google.com/accounts/CheckCookie?chtml=LoginDoneHtml').read()
		
		try:
			sms = self.do_req('https://www.google.com/voice/inbox/recent/sms/').read()
			sp = BeautifulStoneSoup(sms)
			return unicode(sp.response.html.contents[0])
		# This randomly fails for reasons unknown
		except IncompleteRead, e:
			return None

	def parse_result(self, result):
		# the Voice HTML seems to have an extra closing div?
		# this replacement fixes it for BeautifulSoup's parser
		cleaned = result.replace('</div></div></div></div></div>', '</div></div></div></div>')
		sp = BeautifulSoup(cleaned)
		
		# parse SMS threads
		sms = sp.findAll('div', attrs={'class':'goog-flat-button gc-message gc-message-sms'})
		for thread in sms:
			id = thread['id']
			# find all message rows
			rows = thread.findAll('div', attrs={'class':'gc-message-sms-row'})
			# if there looks like there's a new message here
			if not self.convo_threads[id] or len(rows) != len(self.convo_threads[id]):
				start_index = 0 
				for message in rows:
					from_name = message.findAll('span', attrs={'class':'gc-message-sms-from'})[0].string.strip()[:-1]
					message_txt = message.findAll('span', attrs={'class':'gc-message-sms-text'})[0].string.strip()
					identifier = from_name + ' ' + message_txt
					if identifier not in self.convo_threads[id]:
						# new message!
						self.convo_threads[id].add(identifier)
						if from_name != 'Me':
							if self.listeners and len(self.listeners) > 0:
								for listener in self.listeners:
									listener.on_notification('SMS', from_name, message_txt)
						# debug: print message_txt
		
	def get_voicemails(self):
		# if we haven't acquired cookies yet
		if len(self.cookies) == 0:
			 # first do the login POST
			login = self.do_req('https://www.google.com/accounts/ServiceLoginBoxAuth?Email=%s&Passwd=%s&service=grandcentral' % (self.username, self.password)).read()
			 # second step is to pass the cookie check
			cookie_check = self.do_req('https://www.google.com/accounts/CheckCookie?chtml=LoginDoneHtml').read()
		try:
			html = self.do_req('https://www.google.com/voice/inbox/recent/voicemail/').read()
			sp = BeautifulStoneSoup(html)
			return unicode(sp.response.html.contents[0])
		# This randomly fails for reasons unknown
		except IncompleteRead, e:
			return None
	def parse_voicemails(self, result):
		cleaned = result.replace('</div></div></div></div></div>', '</div></div></div></div>')
		sp = BeautifulSoup(cleaned)
		voicemails = sp.findAll('div', attrs={'class':'goog-flat-button gc-message gc-message-unread'})
		for voicemail in voicemails:
			id = voicemail['id']
			# find all voicemail rows
			rows = voicemail.findAll('table', attrs={'class':'gc-message-tbl'})
			for message in rows:
				try:
					from_name = message.findAll('a', attrs={'class':'gc-under gc-message-name-link'})[0].string.strip()
				except:
					from_name = message.findAll('span', attrs={'title':''})[0].string.strip()
				span_array = message.findAll('div', attrs={'class':'gc-message-message-display'})[0].findAll('span', attrs={'class':'gc-word-high'})
				voicemail_transcript_array = []
				for word in span_array:
					voicemail_transcript_array.append(word.string.strip())
				voicemail_transcript = ' '.join(voicemail_transcript_array)
				empty_voicemail_transcript = False
				if voicemail_transcript == '' and not self.convo_threads.has_key(id):
					empty_voicemail_transcript = True
					self.convo_threads[id].add('sentinelemptyvalue')
				elif self.convo_threads.has_key(id) and self.convo_threads[id] == set(['sentinelemptyvalue']):
					del self.convo_threads[id]
				if not self.convo_threads.has_key(id) and not empty_voicemail_transcript:
					self.convo_threads[id].add(id)
					if from_name != 'Me':
						if self.listeners and len(self.listeners) > 0:
							for listener in self.listeners:
								listener.on_notification('Voicemail', from_name, voicemail_transcript)
		
	def check(self):
		feed = self.get_inbox()
		if feed != None:
			feed = feed.replace("<![CDATA[", "")
			feed = feed.replace("]]>", "")
			self.parse_result(feed)
			vmfeed = self.get_voicemails()
			if vmfeed != None:
				vmfeed = vmfeed.replace("<![CDATA[", "")
				vmfeed = vmfeed.replace("]]>", "")
				self.parse_voicemails(vmfeed)
				out_fl = open(self.picklefile, 'w')
				pickle.dump(self.convo_threads, out_fl)
