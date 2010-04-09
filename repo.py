# -*- coding: utf-8 -*-

import pygtk
pygtk.require( '2.0' )
import gtk

class StubRepo:
	name = "Stub"
	owner = "Me"
	description = "A Stub Repo"

	repos = [
		[ "Pongo", "jmhobbs", "PyGTK interface to MongoDB" ],
		[ "MkLst", "jmhobbs", "Dead simple lists." ],
		[ "q-aargh", "jmhobbs", "Attach digital data to real world objects." ],
		[ "poseurhttp", "abraham", "PHP library for making HTTP connections with cURL" ],
		[ "storytlr", "eschnou", "The core of the Storytlr platform" ],
		[ "mf", "stuartherbert", "Methodosity Framework for PHP" ]
	]

	def __init__ ( self ):
		import random
		sample = random.sample( self.repos, 1 )
		self.name = sample[0][0]
		self.owner = sample[0][1]
		self.description = sample[0][2]

class Repo ( gtk.Frame ):

	name = ''
	owner = ''
	description = ''
	revision = ''

	def __init__ ( self, repository, clip=40 ):
		gtk.Frame.__init__( self )

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

		self.add( table )

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