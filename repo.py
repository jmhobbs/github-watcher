# -*- coding: utf-8 -*-

import time
import datetime

import random

import os

import pygtk
pygtk.require( '2.0' )
import gtk, gobject

import git

from multiprocessing import Process, Queue
from Queue import Empty

from traceback import format_exc

def git_sync ( queue, sync_path, repo_name, uri ):
	"""
	Sync the repo on the file system.

	Arguments:
	  - queue     : A Queue to pass messages back to the main process with.
	  - sync_path : The root of the sync directory. Must end in "/"
	  - repo_name : The name of the repository (folder name to sync to)
	  - uri       : The clone-able URI
	"""
	full_path = sync_path + repo_name
	if os.path.exists( full_path ):
		queue.put( [ "FETCH", repo_name ] )
		try:
			repo = git.Repo( full_path )
			repo.remotes.origin.fetch()
			queue.put( [ "FETCHED", repo_name ] )
		except:
			queue.put( [ "FAILED", repo_name ] )
	else:
		queue.put( [ "CLONE", repo_name ] )
		try:
			repo = git.Git().clone( uri, full_path )
			queue.put( [ "CLONED", repo_name ] )
		except:
			queue.put( [ "FAILED", repo_name ] )

class Repo ( gtk.Frame ):

	name = ''
	owner = ''
	description = ''
	cloning = False
	fetching = False
	last_sync = 0

	def __init__ ( self, repository, do_sync, sync_path, sync_interval, sync_own, username, clip=40 ):
		"""
		Create the Repo Widget.

		Arguments:
		  - repository    : A repository object from GitPython
		  - do_sync       : Boolean, True to run sync's, False to not.
		  - sync_path     : The FS path to sync to.
		  - sync_interval : How often to sync, in seconds.
		  - sync_own      : Boolean, True to sync when username == repo.owner
		  - username      : GitHub username of the client user
		  - clip          : How long to clip the repo description at.
		"""
		gtk.Frame.__init__( self )

		self.do_sync = do_sync
		self.sync_own = sync_own
		self.username = username

		self.sync_path = sync_path
		self.sync_interval = sync_interval

		self.name = repository.name
		self.owner = repository.owner
		# A description is not always guaranteed.
		try:
			self.description = repository.description
		except:
			self.description = '(No Description)'

		table = gtk.Table( 4, 2 )
		table.set_col_spacings( 3 )
		table.set_row_spacings( 3 )

		# ROW
		label = gtk.Label( "<b><u>" + self.name + "</u></b>" )
		label.set_alignment( 0, 1 )
		label.set_use_markup( True )
		table.attach( label, 0, 2, 0, 1, gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 2, 2 )

		# ROW
		label = gtk.Label( '<b>Owner:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 0, 1, 1, 2, 0, 0, 2, 2 )

		label = gtk.Label( self.owner )
		label.set_use_markup( True )
		label.set_alignment( 0, 1 )
		table.attach( label, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 2, 2 )

		# ROW
		label = gtk.Label( '<b>About:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 0, 1, 2, 3, 0, 0, 2, 2 )

		desc = self.description
		if len( desc ) > clip:
			desc = desc[:clip-3] + '...'

		label = gtk.Label( desc )
		label.set_use_markup( True )
		label.set_alignment( 0, 1 )
		table.attach( label, 1, 2, 2, 3, gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 2, 2 )

		# ROW
		label = gtk.Label( '<b>State:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 0, 1, 3, 4, 0, 0, 2, 2 )

		self.state_label = gtk.Label( "<span foreground=\"#8000FF\">Sync Pending</span>" )
		self.state_label.set_use_markup( True )
		self.state_label.set_alignment( 0, 1 )
		table.attach( self.state_label, 1, 2, 3, 4, gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 2, 2 )

		self.add( table )

		self.git_process = None
		self.git_queue = Queue()

		# I sync is enabled, start the timers
		if self.do_sync and ( self.sync_own or self.owner != self.username ):
			self.queue_timer = gobject.timeout_add( 250, self.check_queue )
			self.sync_timer = None
			timeout = 1000 * random.randint( 5, 20 )
			self.one_shot = gobject.timeout_add( timeout, self.sync )
		else:
			self.state_label.set_markup( "<span foreground=\"#00C5CC\">Sync Disabled</span>" )

	def sync ( self ):
		"""
		Start the external process to clone or fetch the repository.
		"""
		if None != self.git_process and self.git_process.is_alive():
		 return True
		self.git_process = Process( target=git_sync, args=( self.git_queue, self.sync_path, self.name, "git://github.com/%s/%s.git" % ( self.owner, self.name ) ) )
		self.git_process.daemon = True
		self.git_process.start()

		# We use a one-shot timer to stagger the repo-syncs, so here we need to start the real timer
		if self.sync_timer == None:
			self.sync_timer = gobject.timeout_add( 1000 * self.sync_interval, self.sync )
			return False
		else:
			return True

	def check_queue ( self ):
		"""
		Checks the external process message queue.
		"""
		try:
			while True:
				item = self.git_queue.get( False )
				if "FETCH" == item[0]:
					self.fetch_start()
				elif "FETCHED" == item[0]:
					self.fetch_end( True )
				elif "CLONE" == item[0]:
					self.clone_start()
				elif "CLONED" == item[0]:
					self.clone_end( True )
				elif "FAILED" == item[0]:
					if self.cloning:
						self.clone_end( False )
					else:
						self.sync_end( False )
				else:
					print "Unknown Git Command:", item[0]
		except Empty, e:
			pass
		except Exception, e:
			print e
			print format_exc()
			pass

		return True

	def clone_start ( self ):
		"""
		GUI manipulation on clone start.
		"""
		self.cloning = True
		now = datetime.datetime.now()
		self.state_label.set_markup( "<span foreground=\"#FFBF00\">Cloning... - %s</span>" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )

	def clone_end ( self, success=False ):
		"""
		GUI manipulation on clone end.
		"""
		self.cloning = False
		now = datetime.datetime.now()
		if success:
			self.state_label.set_markup( "<span foreground=\"#00BF00\">Cloning Complete - %s</span>" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
		else:
			self.state_label.set_markup( "<span foreground=\"#BF0303\">Cloning Failed - %s</span>" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
		self.last_sync = time.mktime( now.timetuple() )

	def fetch_start ( self ):
		"""
		GUI manipulation on clone start.
		"""
		self.fetching = True
		now = datetime.datetime.now()
		self.state_label.set_markup( "<span foreground=\"#FFBF00\">Fetching... - %s</span>" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )

	def fetch_end ( self, success=False ):
		"""
		GUI manipulation on fetch end.
		"""
		self.fetching = False
		now = datetime.datetime.now()
		if success:
			self.state_label.set_markup( "<span foreground=\"#00BF00\">Fetch Complete - %s</span>" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
		else:
			self.state_label.set_markup( "<span foreground=\"#BF0303\">Fetch Failed - %s</span>" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
		self.last_sync = time.mktime( now.timetuple() )
