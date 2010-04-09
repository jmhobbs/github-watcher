# -*- coding: utf-8 -*-

import pygtk
pygtk.require( '2.0' )
import gtk

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

	def set_repo_count ( self, count ):
		self.repo_count.set_text( "%d" % count )

	def set_last_update ( self, when ):
		self.last_update.set_text( when )
	
	def set_next_update ( self, when ):
		self.next_update.set_text( when )