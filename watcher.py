# -*- coding: utf-8 -*-

# http://packages.python.org/GitPython/tutorial.html#tutorial-toplevel
# http://packages.python.org/GitPython/reference.html#api-reference-toplevel
# http://github.com/dustin/py-github
# http://develop.github.com/p/users.html

import github.github as github
import git

import pygtk
pygtk.require( '2.0' )
import gtk, gobject

#print "Cloning First Repository"
#git.Git().clone( "git://github.com/%s/%s.git" % ( repos[0].owner, repos[0].name ) )

#gh = github.GitHub()
#repos = gh.repos.watched( 'jmhobbs' )
#for repo in repos:
	#self.add_repo( repo )

class Repo ( gtk.Frame ):

	name = ''
	owner = ''
	description = ''
	revision = ''

	def __init__ ( self, repository ):
		gtk.Frame.__init__( self )
		
		self.name = repository.name
		self.owner = repository.owner
		self.description = repository.description
		
		table = gtk.Table( 2, 4 )
		table.set_col_spacings( 5 )
		table.set_row_spacings( 5 )
		
		label = gtk.Label( '<b>Name:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 0, 1, 0, 1 )
		label = gtk.Label( self.name )
		label.set_use_markup( True )
		label.set_alignment( 0, 1 )
		table.attach( label, 1, 2, 0, 1 )
		
		label = gtk.Label( '<b>Owner:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 2, 3, 0, 1 )
		label = gtk.Label( self.owner )
		label.set_use_markup( True )
		label.set_alignment( 0, 1 )
		table.attach( label, 3, 4, 0, 1 )
		
		self.add( table )

class Console ( gtk.Frame ):

	def __init__ ( self, username ):
		gtk.Frame.__init__( self )
		
		table = gtk.Table( 2, 4 )
		table.set_col_spacings( 5 )
		table.set_row_spacings( 5 )
		
		label = gtk.Label( '<b>User:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 0, 1, 0, 1 )
		label= gtk.Label( username )
		label.set_use_markup( True )
		label.set_alignment( 0, 1 )
		table.attach( label, 1, 2, 0, 1 )
		
		label = gtk.Label( '<b>Last Update:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 2, 3, 0, 1 )
		self.last_update = gtk.Label( "0000-00-00 00:00:00" )
		self.last_update.set_use_markup( True )
		self.last_update.set_alignment( 0, 1 )
		table.attach( self.last_update, 3, 4, 0, 1 )
		
		label = gtk.Label( '<b>Repos Watched:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 0, 1, 1, 2 )
		self.repo_count = gtk.Label( "0" )
		self.repo_count.set_alignment( 0, 1 )
		table.attach( self.repo_count, 1, 2, 1, 2 )
		
		label = gtk.Label( '<b>Next Update:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 2, 3, 1, 2 )
		self.next_update = gtk.Label( "0000-00-00 00:00:00" )
		self.next_update.set_alignment( 0, 1 )
		table.attach( self.next_update, 3, 4, 1, 2 )
		
		self.add( table )

	def set_last_update ( self, when ):
		self.last_update.set_text( when )
	
	def set_next_update ( self, when ):
		self.next_update.set_text( when )

class Watcher:
	def __init__ ( self, username, interval, sync, directory ):

		self.username = username
		self.interval = interval
		self.sync = sync
		self.sync_directory = directory

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
		self.window.set_size_request( 400, 200 )
		
		self.repos = gtk.VBox()
		
		scroll = gtk.ScrolledWindow()
		scroll.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		scroll.add_with_viewport( self.repos )
		
		self.console = Console( self.username )
		
		self.status = gtk.Statusbar()
		
		vbox = gtk.VBox()
		vbox.pack_start( self.console, False, False, 0 )
		vbox.pack_end( self.status, False, False, 0 )
		vbox.pack_end( scroll, True, True, 0 )
		
		self.set_status( 'Welcome to GitHub Watcher!' )
		
		self.window.add( vbox )
		self.window.show_all()
		
		# Initial load of repos
		self.set_status( 'Loading repository list...' )
		self.gh = github.GitHub()
		repos = self.gh.repos.watched( self.username )
		for repo in repos:
			self.add_repo( repo )
		self.set_status( 'Repository list loaded.' )
		# Start the update timer
		#self.timer_id = gobject.timeout_add( 1000 * self.interval, self.update )

	def update ( self ):
		# TODO!
		return

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

	# Add a repo to the window
	def add_repo ( self, repository ):
		repo = Repo( repository )
		#repo.set_size_request( 100, 100 )
		self.repos.pack_start( repo, False, False, 2 )
		repo.show_all()
	
	# Run gtk!
	def main( self ):
		gtk.main()

if __name__ == "__main__":
	import ConfigParser
	config = ConfigParser.RawConfigParser()
	config.read( 'config.ini' )

	app = Watcher( 
		config.get( 'User', 'username' ),
		config.getint( 'API', 'interval' ),
		config.getboolean( 'Other', 'sync' ),
		config.get( 'Other', 'sync-dir' )
	)
	app.main()