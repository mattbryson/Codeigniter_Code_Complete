#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CI custom classes auto complete generation
#
import os, sys, argparse, glob, errno, shutil, re
from collections import namedtuple
from stat import *

#This dir location..
self_dir = os.path.abspath(os.path.dirname(sys._getframe(0).f_code.co_filename))

#Codeigniter site location (set as -c arg when running script)
ci_dir = ''


# Finds the models and controllers dirs in an MVC triad location
def findmvc (top, callback):
	models_dir = os.path.join( top, 'models')
	controllers_dir = os.path.join( top, 'controllers')
	
	walktree(models_dir, callback)
	walktree(controllers_dir, callback)


# Finds all the modules loaded under an HMVC framework
def findmodules(top, callback):
	
	for f in os.listdir(top):
		pathname = os.path.join(top, f)
		mode = os.stat(pathname)[ST_MODE]
		if S_ISDIR(mode):
			 # It's a directory or MVC triad, recurse into it
			findmvc(pathname, callback)
		else:
			# Unknown file type, print a message
			print 'Ignoring %s' % pathname 

# Recursively walk tree looking for php classes
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

# Parse a php class, and make a code hint copy of it
def parsefile(filepath):
#    print 'Analysing', file
    
    #Resolve path to new code-complete file
    cc_filepath = filepath.replace(ci_dir, self_dir)
#    print 'Creating file : ', cc_filepath
    #Get the dir path for the new file
    dirs = os.path.split(cc_filepath)[0]
    #Make dir structure
    try: os.makedirs(dirs, 0777)
    except OSError as err:
        # Reraise the error unless it's about an already existing directory 
        if err.errno != errno.EEXIST or not os.path.isdir(dirs): 
            raise
    
    # Class open bracket
    class_open_bracket = '{'
    class_close_bracket = '}'
    php_tag = '<?php'
    
    #Open out files (and create the out file)
    in_file = open(filepath, 'r')
    out_file = open(cc_filepath, 'w+')
 
    for line in in_file:
	    if re.match("^(?!.*[\*,/,',\"]).*class .*$", line):
			print line,
			
			#Check if we need to add the php tag, and start the class..
			if class_open_bracket not in line:
			    line = ''.join([line,' ',class_open_bracket])
			
			if php_tag not in line:
			    line = ''.join([php_tag,' ',line])
			    
			out_file.write(line)
			break


    #Close the class
    out_file.write(class_close_bracket)
    
    in_file.close()
    out_file.close()

# log errors    
def die(msg):
    print msg
    sys.exit(1)


# main entry point.
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

    generated_files = os.path.join(self_dir, 'application')
    if( os.path.exists( generated_files )):
    	shutil.rmtree( generated_files )
    
    
    findmvc(applicaiton_dir, parsefile)   
    findmodules(modules_dir, parsefile)
    
	
	
	
# go	
if __name__ == '__main__':
	main()




