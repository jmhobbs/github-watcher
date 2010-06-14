# -*- coding: utf-8 -*-

import time
import datetime

import random

import os

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

class Repo:

	name = ''
	owner = ''
	description = ''
	cloning = False
	fetching = False
	last_sync = 0

	def __init__ ( self, repository, do_sync, sync_path, sync_interval, sync_own, username ):
		"""
		Create the Repo Widget.

		Arguments:
		  - repository    : A repository object from GitPython
		  - do_sync       : Boolean, True to run sync's, False to not.
		  - sync_path     : The FS path to sync to.
		  - sync_interval : How often to sync, in seconds.
		  - sync_own      : Boolean, True to sync when username == repo.owner
		  - username      : GitHub username of the client user
		"""
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

		self.git_process = None
		self.git_queue = Queue()

	def sync ( self ):
		"""
		Start the external process to clone or fetch the repository.
		"""
		if None != self.git_process and self.git_process.is_alive():
		 return True
		self.git_process = Process( target=git_sync, args=( self.git_queue, self.sync_path, self.name, "git://github.com/%s/%s.git" % ( self.owner, self.name ) ) )
		self.git_process.daemon = True
		self.git_process.start()

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
		self.cloning = True

	def clone_end ( self, success=False ):
		self.cloning = False 
		self.last_sync = time.mktime( datetime.datetime.now().timetuple() )

	def fetch_start ( self ):
		self.fetching = True

	def fetch_end ( self, success=False ):
		self.fetching = False
		self.last_sync = time.mktime( datetime.datetime.now().timetuple() )
