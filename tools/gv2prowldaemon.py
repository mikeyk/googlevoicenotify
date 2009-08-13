#!/usr/bin/env python2.3
#
#  gv2prowldaemon.py
#  gv2prowl
#
#  Created by Brian Baughman on 7/30/09.
#
from googlevoicenotify import GoogleVoiceNotify
from time import sleep
from getpass import getpass
from prowlgooglevoice import ProwlListener,PrintListener, readparams
import sys, os
from daemon import Daemon
from os import environ

class gv2prowl(Daemon):
  def setpickle(self,pfile=environ['HOME']+'/logs/pickle.dump'):
    self.pfile=pfile
  def setcfile(self,cfile=environ['HOME']+'/.gvnotify'):
    self.cfile=cfile
  def reset(self):
    self.loggedin=False
  def login(self):
    self.loggedin=False
    try:
      self.prowl_listener = ProwlListener()
      self.print_listener = PrintListener()
    except:
      print 'Could not load Listeners...not logged in.'
      self.loggedin=False
      return self.loggedin
    try:
      self.sleep_time, name, passwd = readparams(self.cfile)
    except:
      print 'Could not load Google Voice info...not logged in.'
      self.loggedin=False
      return self.loggedin
    self.gv = GoogleVoiceNotify(name, passwd,\
       listeners=(self.prowl_listener, self.print_listener),\
       picklefile=self.pfile)
    try:
      self.gv = GoogleVoiceNotify(name, passwd,\
       listeners=(self.prowl_listener, self.print_listener),\
       picklefile=self.pfile)
    except:
      print 'Cannot connect to Google Voice.'
      self.loggedin=False
      return self.loggedin
    del passwd
    try:
      self.gv.check()
      self.loggedin=True
    except:
      self.loggedin=False
      return self.loggedin
    print 'Connected will check every %i s'%self.sleep_time
    return self.loggedin
  def run(self):
    if self.loggedin:
      while True:
        self.gv.check()
        sleep(self.sleep_time)
    else:
      print 'Not logged into GV!'

if __name__ == "__main__":
  # This should be turned into an argument with default or something user setable
  logdir=environ['HOME']+'/logs'
  daemon = gv2prowl(logdir+'/gv2prowl.pid',\
   stdin='/dev/null', stdout=logdir+'/gv2prowl.log',\
    stderr=logdir+'/gv2prowl.err')
  daemon.setpickle()
  daemon.setcfile()
  try:
    daemon.loggedin
  except:
    daemon.reset()
  if len(sys.argv) == 2:
    if 'start' == sys.argv[1]:
      daemon.login()
      if daemon.loggedin==True:
        daemon.start()
      else:
        print "Cannot login to Google Voice."
    elif 'stop' == sys.argv[1]:
      daemon.stop()
    elif 'restart' == sys.argv[1]:
      if daemon.loggedin!=True:
        daemon.login()
      daemon.restart()
    elif 'login' == sys.argv[1]:
      daemon.login()
    else:
      print "Unknown command"
      sys.exit(2)
    sys.exit(0)
  else:
    print "usage: %s start|stop|restart" % sys.argv[0]
    sys.exit(2)
