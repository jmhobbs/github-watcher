# -*- coding: utf-8 -*-

# http://packages.python.org/GitPython/tutorial.html#tutorial-toplevel
# http://packages.python.org/GitPython/reference.html#api-reference-toplevel
# http://github.com/dustin/py-github
# http://develop.github.com/p/users.html

#import github.github as github
#import git

#print "Fetching Watched Repository List"
#gh = github.GitHub()
#repos = gh.repos.watched( 'jmhobbs' )
#print "Cloning First Repository"
#git.Git().clone( "git://github.com/%s/%s.git" % ( repos[0].owner, repos[0].name ) )

import pygtk
pygtk.require( '2.0' )
import gtk, gobject


class Repo ( gtk.Frame ):

	def __init__ ( self ):
		gtk.Frame.__init__( self )

class Console ( gtk.Frame ):

	def __init__ ( self ):
		gtk.Frame.__init__( self )
		
		table = gtk.Table( 2, 4 )
		table.set_col_spacings( 5 )
		
		label = gtk.Label( '<b>User:</b>' )
		label.set_use_markup( True )
		label.set_alignment( 1, 1 )
		table.attach( label, 0, 1, 0, 1 )
		label= gtk.Label( "jmhobbs" )
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

class Watcher:
	def __init__ ( self ):
		#gtk.window_set_default_icon_from_file( 'images/icon_16s.png' )
		self.window = gtk.Window( gtk.WINDOW_TOPLEVEL )
		self.window.connect( "destroy", lambda w: gtk.main_quit() )
		self.window.set_title( "GitHub Watcher" )
		self.window.set_size_request( 400, 200 )
		
		self.repos = gtk.VBox()
		
		scroll = gtk.ScrolledWindow()
		scroll.set_policy( gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC )
		scroll.add_with_viewport( self.repos )
		
		self.status = Console()
		
		vbox = gtk.VBox()
		vbox.pack_start( self.status, False, False, 0 )
		vbox.pack_end( scroll, True, True, 0 )
		
		self.window.add( vbox )
		self.window.show_all()

	def add_repo ( self ):
		repo = Repo()
		repo.set_size_request( 100, 100 )
		self.repos.pack_start( repo, False, False, 0 )
		repo.show()

	def main( self ):
		gtk.main()

if __name__ == "__main__":
	app = Watcher()
	app.main()