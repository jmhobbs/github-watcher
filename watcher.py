# -*- coding: utf-8 -*-

# http://packages.python.org/GitPython/tutorial.html#tutorial-toplevel
# http://packages.python.org/GitPython/reference.html#api-reference-toplevel
# http://github.com/dustin/py-github
# http://develop.github.com/p/users.html

import github.github as github
import git

print "Fetching Watched Repository List"
gh = github.GitHub()
repos = gh.repos.watched( 'jmhobbs' )
print "Cloning First Repository"
git.Git().clone( "git://github.com/%s/%s.git" % ( repos[0].owner, repos[0].name ) )