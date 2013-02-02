#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CI custom classes auto complete generation
#
import os, sys, argparse, glob, errno, shutil
from collections import namedtuple
from stat import *

self_dir = os.path.abspath(os.path.dirname(sys._getframe(0).f_code.co_filename))
ci_dir = ''



def walk_mvc (top, callback):
	models_dir = os.path.join( top, 'models')
	controllers_dir = os.path.join( top, 'controllers')
	
	walktree(models_dir, callback)
	walktree(controllers_dir, callback)


def walk_modules(top, callback):
	
	for f in os.listdir(top):
		pathname = os.path.join(top, f)
		mode = os.stat(pathname)[ST_MODE]
		if S_ISDIR(mode):
			 # It's a directory or MVC triad, recurse into it
			walk_mvc(pathname, callback)
		else:
			# Unknown file type, print a message
			print 'Ignoring %s' % pathname 

def walktree(top, callback):
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file'''

    for f in os.listdir(top):
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[ST_MODE]
        if S_ISDIR(mode):
            # It's a directory, recurse into it
            walktree(pathname, callback)
        elif S_ISREG(mode):
            # It's a php file, call the callback function
            if(pathname.endswith('.php')):
            	callback(pathname)
            else:
            	print 'Ignoring %s' % pathname 
        else:
            # Unknown file type, print a message
            print 'Ignoring %s' % pathname

def parsefile(file):
    print 'analysing', file
    
    #OPen and read orig file
    #    file = open(file, 'r')
    
    

    out_file = file.replace(ci_dir, self_dir)
    print 'creating file', out_file
    dirs = os.path.split(out_file)[0]

    try: os.makedirs(dirs, 0777)
    except OSError as err:
        # Reraise the error unless it's about an already existing directory 
        if err.errno != errno.EEXIST or not os.path.isdir(dirs): 
            raise

    file = open(out_file, 'w+')
    file.close()
    
def die(msg):
    print msg
    sys.exit(1)

	
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--codeigniter', default='../www', help='path to codeigniter installation relative to codecomplete')
    args = parser.parse_args()
    
	# Full System and Application directories locations
    global ci_dir
    ci_dir = os.path.abspath(os.path.join(self_dir, args.codeigniter));
    system_dir = os.path.abspath(os.path.join(self_dir, args.codeigniter, 'system'))
    applicaiton_dir = os.path.abspath(os.path.join(self_dir, args.codeigniter, 'application'))
    modules_dir = os.path.abspath(os.path.join(self_dir, args.codeigniter, 'application', 'modules'))

    print applicaiton_dir
    print modules_dir
    print ci_dir
    print self_dir
    
    generated_files = os.path.join(self_dir, 'application')
    if( os.path.exists( generated_files )):
    	shutil.rmtree( generated_files )
    
    
    walk_mvc(applicaiton_dir, parsefile)   
    walk_modules(modules_dir, parsefile)
    
	
	
	
	
if __name__ == '__main__':
	main()




