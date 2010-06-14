# -*- coding: utf-8 -*-

# This file is the command line interface to the github-watcher daemon.

# Copyright (c) 2010 John Hobbs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import socket
import os, os.path

class GithubWatcher:

	def __init__ ( self ):
		self.socket_file = config.get( 'General', 'socket' )
		if not os.path.exists( self.socket_file ):
			raise Exception( "Socket File Not Found" )
		
		self.socket = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
		self.socket.connect( self.socket_file )

	def __del__ ( self ):
		self.socket.close()

if __name__ == "__main__":
	import sys
	from optparse import OptionParser
	import ConfigParser

	# Go to our default path
	os.chdir( sys.path[0] )
	if sys.path[0] != os.getcwd():
		print "ERROR: Could not change directory to %s." % sys.path[0]
		exit()

	config = ConfigParser.RawConfigParser()
	config.read( 'config.ini' )
	
	parser = OptionParser(
		usage="usage: %prog [options] ACTION",
		version="%prog 0.1",
		description="Shows state information of the github-watcher daemon."
	)
	parser.add_option( "-f", "--file", dest="filename", help="write report to FILE", metavar="FILE")
	parser.add_option( "-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
	
	(options, args) = parser.parse_args()
	
	app = GithubWatcher( config )