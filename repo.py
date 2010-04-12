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

def git_fetch ( queue, sync_path, repo_name, uri ):
	full_path = sync_path + repo_name
	if os.path.exists( full_path ):
		queue.put( [ "PULL", repo_name ] )
		try:
			repo = git.Repo( full_path )
			repo.remotes.origin.pull()
			queue.put( [ "PULLED", repo_name ] )
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
	syncing = False
	last_sync = 0

	def __init__ ( self, repository, do_sync, sync_path, sync_interval, sync_own, username, clip=40 ):
		gtk.Frame.__init__( self )

		self.do_sync = do_sync
		self.sync_own = sync_own
		self.username = username

		self.sync_path = sync_path
		self.sync_interval = sync_interval

		self.name = repository.name
		self.owner = repository.owner
		self.description = repository.description

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
		
		self.state_label = gtk.Label( "Sync Pending" )
		self.state_label.set_alignment( 0, 1 )
		table.attach( self.state_label, 1, 2, 3, 4, gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL, 2, 2 )

		self.add( table )
		
		self.git_process = None
		self.git_queue = Queue()
		
		if self.do_sync and ( self.sync_own or self.owner != self.username ):
			self.queue_timer = gobject.timeout_add( 250, self.check_queue )
			self.sync_timer = gobject.timeout_add( 1000 * self.sync_interval, self.sync )
			self.sync()
		else:
			self.state_label.set_text( "Sync Disabled" )

	def sync ( self ):
		if None != self.git_process and self.git_process.is_alive():
		 return True
		self.git_process = Process( target=git_fetch, args=( self.git_queue, self.sync_path, self.name, "git://github.com/%s/%s.git" % ( self.owner, self.name ) ) )
		self.git_process.daemon = True
		self.git_process.start()

	def check_queue ( self ):
		try:
			while True:
				item = self.git_queue.get( False )
				if "PULL" == item[0]:
					self.sync_start()
				elif "PULLED" == item[0]:
					self.sync_end( True )
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
		self.cloning = True
		now = datetime.datetime.now()
		self.state_label.set_text( "Cloning... - %s" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
	
	def clone_end ( self, success=False ):
		self.cloning = False
		now = datetime.datetime.now()
		if success:
			self.state_label.set_text( "Cloning Complete - %s" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
		else:
			self.state_label.set_text( "Cloning Failed - %s" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
		self.last_sync = time.mktime( now.timetuple() )
	
	def sync_start ( self ):
		self.syncing = True
		now = datetime.datetime.now()
		self.state_label.set_text( "Pulling... - %s" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
	
	def sync_end ( self, success=False ):
		self.syncing = False
		now = datetime.datetime.now()
		if success:
			self.state_label.set_text( "Pull Complete - %s" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
		else:
			self.state_label.set_text( "Pull Failed - %s" % now.strftime( "%Y-%m-%d %H:%M:%S" ) )
		self.last_sync = time.mktime( now.timetuple() )

if __name__ == "__main__":
	
	class Test:
		def __init__ ( self ):
			self.window = gtk.Window()
			self.window.connect( "destroy", lambda x: gtk.main_quit() )
			
			vbox = gtk.VBox()
			for i in range( 0, 5 ):
				stub = StubRepo()
				repo = Repo( stub )
				vbox.pack_start( repo, False, False, 2 )
			
			self.window.add( vbox )
			self.window.show_all()
		
		def main ( self ):
			gtk.main()
	
	app = Test()
	app.main()