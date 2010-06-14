# -*- coding: utf-8 -*-

# This file is the background daemon for github-watcher.

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

import datetime
import time

import socket
import os, os.path

from multiprocessing import Process, Queue
from Queue import Empty

import github.github as github

class GithubWatcherDaemon:

	def __init__ ( self, config ):
		# Set up our socket
		self.socket_file = config.get( 'General', 'socket' )
		if os.path.exists( self.socket_file ):
			os.remove( self.socket_file )
		self.socket = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
		self.socket.bind( self.socket_file )
		self.username = config.get( 'General', 'username' )
	
	def __del__ ( self ):
		server.close()
		os.remove( self.socket_file )
	
	def main ( self ):
		print "STUB: Main"
	
if __name__ == "__main__":
	import sys

	# Go to our default path
	os.chdir( sys.path[0] )
	if sys.path[0] != os.getcwd():
		print "ERROR: Could not change directory to %s." % sys.path[0]
		exit()

	import ConfigParser
	config = ConfigParser.RawConfigParser()
	config.read( 'config.ini' )

	app = GithubWatcherDaemon( config )
	app.main()