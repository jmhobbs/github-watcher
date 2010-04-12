# -*- coding: utf-8 -*-

# http://packages.python.org/GitPython/tutorial.html#tutorial-toplevel
# http://packages.python.org/GitPython/reference.html#api-reference-toplevel
# http://github.com/dustin/py-github
# http://develop.github.com/p/users.html

import sys
import os
import datetime
import time

from multiprocessing import Process, Queue
from Queue import Empty

import github.github as github

import pygtk
pygtk.require( '2.0' )
import gtk, gobject

from console import Console
from repo import Repo

from traceback import format_exc

def full_path ( path ): # TODO: Cross platform...?
	if "/" != path[0]:
		return sys.path[0] + "/" + path
	else:
		return path

def github_fetch ( queue, username, first_run=False ):
		gh = github.GitHub()
		repos = gh.repos.watched( username )
		if first_run:
			queue.put( [ "LOAD", repos ] )
		else:
			queue.put( [ "UPDATE", repos ] )

class Watcher:
	def __init__ ( self, config ):

		self.config = config

		gtk.window_set_default_icon_from_file( 'icon.16.png' )
		
		# Setup Tray
		self.tray = gtk.status_icon_new_from_file( 'icon.16.png' )
		self.tray.set_tooltip( 'GitHub Watcher' )
		self.tray.connect( 'popup-menu', self.tray_popup )

		self.tray_menu = gtk.Menu()
		menu_item = gtk.MenuItem( "Show" )
		menu_item.connect( "activate", self.show_window )
		menu_item.show()
		
		self.tray_menu.append( menu_item )
		menu_item = gtk.MenuItem( "Quit" )
		menu_item.connect( "activate", self.quit )
		menu_item.show()
		self.tray_menu.append( menu_item )
		
		# Setup Window
		self.window = gtk.Window( gtk.WINDOW_TOPLEVEL )
		self.window.connect( "delete_event", self.hide_window )
		self.window.set_title( "GitHub Watcher" )
		self.window.set_size_request( 600, 400 )
		self.window.set_border_width( 5 )
		
		# Setup repo view
		self.repos = {}
		self.repo_boxes = gtk.VBox()
		scroll = gtk.ScrolledWindow()
		scroll.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		scroll.add_with_viewport( self.repo_boxes )
		
		# Add the console & status bar
		self.console = Console( self.config.get( 'General', 'username' ) )
		self.status = gtk.Statusbar()
		self.set_status( 'Welcome to GitHub Watcher!' )
		
		# Pack it all in
		vbox = gtk.VBox()
		vbox.pack_start( self.console, False, False, 0 )
		vbox.pack_end( self.status, False, False, 0 )
		vbox.pack_end( scroll, True, True, 0 )
		
		self.window.add( vbox )
		self.window.show_all()
		
		# Setup multi-processing
		self.github_process = None
		self.github_queue = Queue()
		self.queue_timer = gobject.timeout_add( 250, self.check_queue )
		
		# Initial load of repos
		self.set_status( 'Loading repository list.' )
		self.github_process = Process( target=github_fetch, args=( self.github_queue, self.config.get( 'General', 'username' ), True ) )
		self.github_process.daemon = True
		self.github_process.start()

		# Start the update timer
		self.update_timer = gobject.timeout_add( 1000 * self.config.getint( 'API', 'interval' ), self.update )
		now = datetime.datetime.now()
		diff = datetime.timedelta( seconds=self.config.getint( 'API', 'interval' ) )
		then = now + diff
		self.console.set_next_update( then.strftime( "%Y-%m-%d %H:%M:%S" ) )

	
	def check_queue ( self ):

		try:
			while True:
				item = self.github_queue.get( False )
				if "LOAD" == item[0]:
					for repo in item[1]:
						self.add_repo( repo )
					keys = sorted( self.repos.keys(), key=lambda x: x.lower() )
					for key in keys:
						self.repo_boxes.pack_start( self.repos[key], False, False, 2 )
						
					self.console.set_repo_count( len( self.repos ) )
					now = datetime.datetime.now()
					self.console.set_last_update( now.strftime( "%Y-%m-%d %H:%M:%S" ) )
					diff = datetime.timedelta( seconds=self.config.getint( 'API', 'interval' ) )
					then = now + diff
					self.console.set_next_update( then.strftime( "%Y-%m-%d %H:%M:%S" ) )
					
					self.set_status( 'Repository list loaded.' )
					
				elif "UPDATE" == item[0]:
					# Deleted
					repo_names = []
					for repo in item[1]:
						repo_names.append( repo.name )

					removed = 0
					for name, obj in self.repos.items():
						if name not in repo_names:
							self.remove_repo( name )
							removed = removed + 1

					# Added 
					repo_names = []
					for name, obj in self.repos.items():
						repo_names.append( name )

					added = 0
					for repo in item[1]:
						if repo.name not in repo_names:
							self.add_repo( repo )
							added = added + 1

					if 0 != added:
						for name,repo in self.repos.items():
							self.repo_boxes.remove( repo )

						keys = sorted( self.repos.keys(), key=lambda x: x.lower() )

						for key in keys:
							self.repo_boxes.pack_start( self.repos[key], False, False, 2 )

					self.console.set_repo_count( len( self.repos ) )
					now = datetime.datetime.now()
					self.console.set_last_update( now.strftime( "%Y-%m-%d %H:%M:%S" ) )
					diff = datetime.timedelta( seconds=self.config.getint( 'API', 'interval' ) )
					then = now + diff
					self.console.set_next_update( then.strftime( "%Y-%m-%d %H:%M:%S" ) )

					self.set_status( 'Repository list updated. +%d -%d' % ( added, removed ) )
					
				else:
					print "Unknown GitHub Command:", item[0]
		except Empty, e:
			pass
		except Exception, e:
			print e
			print format_exc()
			pass
		
		return True

	def update ( self ):
		if self.github_process.is_alive():
		 return True
		self.set_status( 'Updating repository list.' )
		self.github_process = Process( target=github_fetch, args=( self.github_queue, self.config.get( 'General', 'username' ) ) )
		self.github_process.daemon = True
		self.github_process.start()
		return True

	# Raise or show the window
	def show_window ( self, data ):
		self.window.present()

	# Hide the window
	def hide_window ( self, data, other ):
		self.window.hide()
		return True

	# Really quit
	def quit ( self, data ):
		gtk.main_quit()

	# Show the tray menu
	def tray_popup ( self, status, button, time ):
		self.tray_menu.popup( None, None, None, button, time )

	# Set the window status
	def set_status ( self, message ):
		context = self.status.get_context_id( 'status' )
		self.status.pop( context )
		self.status.push( context, message )

	# Add a repo to the stack
	def add_repo ( self, repository ):
		self.repos[ repository.name ] = Repo( 
			repository,
			self.config.getboolean( 'Sync', 'sync' ),
			self.config.get( 'Sync', 'sync-directory' ),
			self.config.getint( 'Sync', 'sync-interval' ),
			self.config.getboolean( 'Sync', 'sync-own' ),
			self.config.get( 'General', 'username' ),
			self.config.getint( 'General', 'description-clip' ),
			)
		self.repos[ repository.name ].show_all()
	
	def remove_repo ( self, repository_name ):
		self.repo_boxes.remove( self.repos[ repository_name ] )
		del self.repos[ repository_name ]
	
	# Run gtk!
	def main( self ):
		gtk.main()

if __name__ == "__main__":
	import ConfigParser
	config = ConfigParser.RawConfigParser()
	config.read( 'config.ini' )

	app = Watcher( config )
	app.main()