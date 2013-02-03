#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Creates a reflection of a codeigniter project, and adds for each class adds 
# comments and data types to enable code completion in IDEs such as eclipse
#
import os, sys, argparse, glob, errno, shutil, re, mmap
from collections import namedtuple
from stat import *

#Codeigniter site location (set as -c arg when running script)
ci_dir = ''


#This dir location..
SELF_DIR = os.path.abspath(os.path.dirname(sys._getframe(0).f_code.co_filename))

#CI directories to scan for classes
CI_DIRS = ['models','controllers','libraries','helpers','core']

#Define our regexs / patterns   
CLASS_OPEN_BRACKET = '{'
CLASS_CLOSE_BRACKET = '}'
PHP_TAG = '<?php'
CLASS_PATTERN = "^(?!.*[\*,/,',\"]).*class .*$"
LOAD_PATTERN = r"(?:load->model|library)(.*?\))"

COMMENT_PATTERN = """/**
 * @var {class}
 */            
var ${var};    
"""



# Finds the models and controllers dirs in an MVC triad location
def findClasses (top, callback):
   for dir in CI_DIRS:
        walktree(os.path.join( top, dir), callback)



# Finds all the modules loaded under an HMVC framework
def findModules(top, callback):
    if(os.path.isdir(top)):
        for f in os.listdir(top):
            pathname = os.path.join(top, f)
            mode = os.stat(pathname)[ST_MODE]
            if S_ISDIR(mode):
		         # It's a directory, find its classes
                findClasses(pathname, callback)
            else:
                # Unknown file type, print a message
                print 'Ignoring ', pathname 


# Recursively walk tree looking for php classes
def walktree(top, callback):
    #recursively descend the directory tree rooted at top,
    #calling the callback function for each regular file
    if(os.path.isdir(top)):
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
                    print 'Ignoring', pathname 
            else:
                # Unknown file type, print a message
                print 'Ignoring', pathname


# Parse a php class, and make a code hint copy of it
def parseFile(filepath):
    print 'Analysing', filepath
    
    #Resolve path to new code-complete file
    cc_filepath = filepath.replace(ci_dir, SELF_DIR)

    #Get the dir path for the new file
    dirs = os.path.split(cc_filepath)[0]
    #Make dir structure
    try: os.makedirs(dirs, 0777)
    except OSError as err:
        # Reraise the error unless it's about an already existing directory 
        if err.errno != errno.EEXIST or not os.path.isdir(dirs): 
            raise
            die("Could not mk dirs")
    
    
    #Open out files (and create the out file)
    in_file = open(filepath, 'r+')
    out_file = open(cc_filepath, 'w+')
    
    file_header = ''
    file_footer = '\n'+CLASS_CLOSE_BRACKET
    file_body = ''
    with in_file as f:
        data = mmap.mmap(f.fileno(), 0)
        
        #Get the Class definition
        mo = re.search(CLASS_PATTERN, data, re.M)
        if mo:
            file_header = mo.group(0)
            #Check if we need to add the php tag, and start the class..
            if CLASS_OPEN_BRACKET not in file_header:
                file_header = ''.join([file_header,' ',CLASS_OPEN_BRACKET])
			
            if PHP_TAG not in file_header:
                file_header = ''.join([PHP_TAG,'\n',file_header])

            
        #Models, Libraries etc
        it1 = re.finditer(LOAD_PATTERN, data, re.M | re.I | re.S)
        for mo1 in it1:
            it2 = re.finditer('\"(.+?)\"|\'(.+?)\'',  mo1.group(1))
            for mo2 in it2:
                #clean the quotes out - cant get the regex above to do this for some reason.
                classpath =  mo2.group(0).replace('\"','').replace('\'','')
                #Split on path delimiters, and take the last element, the class name
                classpath = classpath.split('/')
                classname = classpath[-1]
                
                #write the property out
                file_body = ''.join([file_body, '\n', getComment(classname)])

    #write out the new code complete class
    out_file.write(file_header)
    out_file.write(file_body)
    out_file.write(file_footer)
    
    in_file.close()
    out_file.close()



def getComment(classname):
    comment = COMMENT_PATTERN.replace("{class}", classname.capitalize())
    comment = comment.replace("{var}", classname)
    return comment


# main entry point.
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--codeigniter', default='../www', help='path to codeigniter project relative to codecomplete')
    args = parser.parse_args()
    
	# Full System and Application directories locations
    global ci_dir
    ci_dir = os.path.abspath(os.path.join(SELF_DIR, args.codeigniter));
    system_dir = os.path.abspath(os.path.join(SELF_DIR, args.codeigniter, 'system'))
    applicaiton_dir = os.path.abspath(os.path.join(SELF_DIR, args.codeigniter, 'application'))
    modules_dir = os.path.abspath(os.path.join(SELF_DIR, args.codeigniter, 'application', 'modules'))

    generated_files = os.path.join(SELF_DIR, 'application')
    #Clean old generated files
    if( os.path.exists( generated_files )):
    	shutil.rmtree( generated_files )
    
    
    findClasses(applicaiton_dir, parseFile)   
    findModules(modules_dir, parseFile)
   
    
# log errors    
def die(msg):
    print msg
    sys.exit(1)	
	
	
# go	
if __name__ == '__main__':
	main()




