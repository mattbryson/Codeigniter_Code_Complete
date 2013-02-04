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

#Auto loaded classes that will be included in every class
auto_loads = ''

#This dir location..
SELF_DIR = os.path.abspath(os.path.dirname(sys._getframe(0).f_code.co_filename))

#CI directories to scan for classes
CI_DIRS = ['models','controllers','libraries','helpers','core']


#Define our regexs / patterns   
CLASS_OPEN_BRACKET = '{'
CLASS_CLOSE_BRACKET = '}'
PHP_TAG = '<?php'
CLASS_PATTERN = "^(?!.*[\*,/,',\"]).*class .*$"
LOAD_PATTERN = r"(?:load[\s]*?->[\s]*?model|library)(.*?\))"
AUTOLOAD_PATTERN = r"(?:(?:[^\|[\s]*?]|^)\$autoload\['(?:model|libraries)'\][\s]*?=[\s]*?array[\s]*?)(.*?\))"
CLASS_LIST_PATTERN = '\"(.+?)\"|\'(.+?)\''
COMMENT_PATTERN = """/**
 * @var {class}
 */            
var ${var};    
"""

files_created = 0

FAIL = -1
NORM = 0    
WARN = 1
INFO = 2
TITLE = 3

def msg( str, type=0 ):
    if(type==NORM):
        print  '\033[92m', str, '\033[0m'   
    
    elif( type == WARN ):
        print  '\033[93m', str, '\033[0m'    

    elif ( type == INFO ):
        print  '\033[95m', str, '\033[0m'
        
    elif ( type == TITLE ):
        print  '\033[1m', str, '\033[0m'       
        
    elif( type == FAIL ):
        print  '\033[91m', str, '\033[0m'  
        sys.exit(1)	
        
          

def findAutoLoad(top):
    auto_loads_str=''
    filepath = os.path.join(top, 'config', 'autoload.php')
    if (os.path.exists( filepath )):
        #Open autoload and get loads of models and libraries
        in_file = open(filepath, 'r+')
    
        with in_file as f:
            data = mmap.mmap(f.fileno(), 0)
        
            #Get the Class definition
            it1 = re.finditer(AUTOLOAD_PATTERN, data, re.M | re.I | re.S)
            for mo1 in it1:
                it2 = re.finditer(CLASS_LIST_PATTERN,  mo1.group(1))
                for mo2 in it2:
                    #write the property out
                    auto_loads_str = ''.join([auto_loads_str, '\n', getComment(mo2.group(0))])
    
    return auto_loads_str            
               
            

# Finds the models and controllers dirs in an MVC triad location
def findClasses (top, callback):
    #First get any autoloaded classes, as these will need to be added to
    #each of our individual classes
    global auto_loads
    auto_loads = ''.join( [auto_loads, findAutoLoad(top)] )   
    
    #Check for php classes in the CI folders we are scanning.
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
                msg('Ignoring: ' + pathname, WARN )


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
                    msg('Ignoring: ' + pathname, WARN )
            else:
                # Unknown file type, print a message
                msg('Ignoring: ' + pathname, WARN )


# Parse a php class, and make a code hint copy of it
def parseFile(filepath):
   # msg('Analysing ' + filepath )
    
    #Open out files (and create the out file)
    in_file = open(filepath, 'r+')
    
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
            it2 = re.finditer(CLASS_LIST_PATTERN,  mo1.group(1))
            for mo2 in it2:
                #write the property out
                file_body = ''.join([file_body, '\n', getComment(mo2.group(0))])
    
    global auto_loads  
    if (file_body != '' or auto_loads != ''):
        out_file = cloneFile(filepath)
        #write out the new code complete class
        out_file.write(file_header)
        out_file.write("\n//Class fields")
        out_file.write(file_body)
        if( auto_loads != '' ):
            out_file.write("\n//Auto loaded fields")
            class_file = os.path.split(filepath)[-1]
            class_name = class_file.replace('.php','')
            current_auto_load = auto_loads
            #If the current class is in the auto load, remove it so we dont get cyclical reference
            if( class_name in current_auto_load ):
                current_auto_load = current_auto_load.replace("@var " + class_name, '', re.I)
                current_auto_load = current_auto_load.replace("var $" + class_name.lower() + ";", '', re.I)
            
            out_file.write(current_auto_load)
        
        out_file.write(file_footer)
        out_file.close()
    
    in_file.close()
    

    
    
def cloneFile(filepath):
    #Resolve path to new code-complete file
    cc_filepath = filepath.replace(ci_dir, SELF_DIR)
    makeDir(cc_filepath)
    msg( 'Creating: ' + cc_filepath )
    out_file = open(cc_filepath, 'w+')
    global files_created
    files_created+=1
    return out_file
        

def makeDir(path):
    #Get the dir path for the new file
    dirs = os.path.split(path)[0]
    #Make dir structure
    try: os.makedirs(dirs, 0777)
    except OSError as err:
        # Reraise the error unless it's about an already existing directory 
        if err.errno != errno.EEXIST or not os.path.isdir(dirs): 
            raise
            msg("Could not mk dirs", FAIL)
    


def getComment(classpath):
    
    #clean the quotes out - cant get the regex above to do this for some reason.
    classpath =  classpath.replace('\"','').replace('\'','')
    #Split on path delimiters, and take the last element, the class name
    classpath = classpath.split('/')
    classname = classpath[-1]
                
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
    
    msg('')
    msg('Codeigniter Codecomplete generator', TITLE)
    msg('CI site : ' + ci_dir, INFO)
    
        
    generated_files = os.path.join(SELF_DIR, 'application')
    #Clean old generated files
    if( os.path.exists( generated_files )):
        msg('Removing existing generated files...', INFO)
    	shutil.rmtree( generated_files )
    
    msg('Creating codecomplete files at ' + generated_files, INFO)
    msg('--------------------')
    
    #Also check for autoload.php in the config...
    findClasses(applicaiton_dir, parseFile)   
    findModules(modules_dir, parseFile)
    
    msg('')
    msg('--------------------')
    msg(''.join(["Finished: " ,`files_created`," files created "]))
    msg("Please unsure you have the following path added to your PHP Build path:", TITLE)
    msg(SELF_DIR, INFO)
	
	
# go	
if __name__ == '__main__':
	main()




