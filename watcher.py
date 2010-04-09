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
import git

import pygtk
pygtk.require( '2.0' )
import gtk, gobject

from console import Console
from repo import Repo

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

def git_fetch ( queue, sync_path, repo_name, uri ):
	full_path = sync_path + "/" + repo_name
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

class Watcher:
	def __init__ ( self, username, interval, sync, directory, sync_interval, clip ):

		self.username = username
		self.interval = interval
		self.sync = sync
		self.sync_interval = sync_interval
		self.sync_directory = directory
		self.clip = clip

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
		self.console = Console( self.username )
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
		self.git_process = None
		self.git_queue = Queue()
		self.github_process = None
		self.github_queue = Queue()
		self.queue_timer = gobject.timeout_add( 250, self.check_queues )
		
		# Initial load of repos
		self.set_status( 'Loading repository list.' )
		self.github_process = Process( target=github_fetch, args=( self.github_queue, self.username, True ) )
		self.github_process.daemon = True
		self.github_process.start()

		self.start_timer()

	def start_timer ( self ):
		# Start the update timer
		self.update_timer = gobject.timeout_add( 1000 * self.interval, self.update )
		now = datetime.datetime.now()
		diff = datetime.timedelta( seconds=self.interval )
		then = now + diff
		self.console.set_next_update( then.strftime( "%Y-%m-%d %H:%M:%S" ) )

	
	def check_queues ( self ):
		try:
			while True:
				item = self.git_queue.get( False )
				if "PULL" == item[0]:
					self.repos[item[1]].sync_start()
				elif "PULLED" == item[0]:
					self.repos[item[1]].sync_end( True )
					self.sync_repos()
				elif "CLONE" == item[0]:
					self.repos[item[1]].clone_start()
				elif "CLONED" == item[0]:
					self.repos[item[1]].clone_end( True)
					self.sync_repos()
				elif "FAILED" == item[0]:
					if self.repos[item[1]].cloning:
						self.repos[item[1]].clone_end( False )
					else:
						self.repos[item[1]].sync_end( False )
					self.sync_repos()
				else:
					print "Unknown Git Command:", item[0]
		except Empty, e:
			pass
		except Exception, e:
			from traceback import format_exc
			print e
			print format_exc()
			pass

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
					
					self.set_status( 'Repository list loaded.' )
					self.sync_repos()
					
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

					self.set_status( 'Repository list updated. +%d -%d' % ( added, removed ) )
					self.sync_repos()

				else:
					print "Unknown GitHub Command:", item[0]
		except Empty, e:
			pass
		except Exception, e:
			from traceback import format_exc
			print e
			print format_exc()
			pass
		
		return True

	def update ( self ):
		if self.github_process.is_alive():
		 return True
		self.set_status( 'Updating repository list.' )
		self.github_process = Process( target=github_fetch, args=( self.github_queue, self.username ) )
		self.github_process.daemon = True
		self.github_process.start()
		return False

	def sync_repos ( self ):
		if None != self.git_process and self.git_process.is_alive():
			return False

		for name,repo in self.repos.items():
			if repo.last_sync < time.mktime(datetime.datetime.now().timetuple()) - self.sync_interval:
				self.git_process = Process( target=git_fetch, args=( self.git_queue, self.sync_directory, name, "git://github.com/%s/%s.git" % ( repo.owner, repo.name ) ) )
				self.git_process.daemon = True
				self.git_process.start()
				return

		self.start_timer()


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
		self.repos[ repository.name ] = Repo( repository, self.clip )
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

	app = Watcher( 
		config.get( 'General', 'username' ),
		config.getint( 'API', 'interval' ),
		config.getboolean( 'Sync', 'sync' ),
		config.get( 'Sync', 'sync-dir' ),
		config.getint( 'Sync', 'interval' ),
		config.getint( 'General', 'description-clip' )
	)
	app.main()