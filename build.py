#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CodeComplete for CodeIgniter
# Creates a reflection of a codeIgniter project, and for each class adds 
# comments and data types to enable code completion in IDEs such as eclipse
#
# Supports the following structures
# $this->load->model('my_model');
# $this -> load -> model('my_package/my_model');
# $this->load->model(array('my_model', 'my_other_model'));
# $this->load->model(
#    array(
#       'my_model', 
#       'my_other_model'
#   ));
# $this->CI =& get_instance();
# $this->CI->load->model('my_model');
#
# $CI =& get_instance();
# $CI->load->model('my_model');
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
CI_DIRS = ['models','controllers','libraries','helpers','core', 'hooks']


#Define our regexs / patterns   
CLASS_OPEN_BRACKET = '{'
CLASS_CLOSE_BRACKET = '}'
PHP_TAG = '<?php'
CLASS_PATTERN = "^(?!.*[\*,/,',\"]).*class .*$"

LOAD_PATTERN = r"^[\s]*?[^//,*][\s]*?\$([^\s\\]*?)(?:->[\s]*?load[\s]*?->[\s]*?(?:model|library))(.*?\))"
# r                             python escape for regex
# ^[\s]*?[^//,*][\s]*?          start of line, allow 0 or more spaces then NO comment //, or * then 0 or more spaces
# \$                            find string starting with dollar
# (                             start a capturing match
# [^\s\\]                       That has any character excluding white space
# *?                            0 or more times with no greedy match (so until next found letter in the rex ex)
# )                             Close capturing match
# (?:                           start a non capturing match
# ->[\s]*?load[\s]*?->[\s]*?    find the string '->' then whitespace 0 or more times then 'load' the white space 0 or more times then '->' the white space 0 or more times
# (?:                           start non capturing match
# model|library                 then find the string 'model' OR 'library' 
# )                             close non capturing match
# )                             close non capturing match
# (                             Start a capturing match
#.*?\)                          Look for any character (.) 0 or more times (*) non greedy (?) leading up to a close bracket \) (escaped)
#)                              Close returning match.
#
# this will return  (array('my_model','anonther_model'))  from 
# $this -> load -> model( array('my_model','anonther_model' ));  
# or ('my_library') from
# $this->load->library('my_library');
 

AUTOLOAD_PATTERN = r"(?:(?:[^\|[\s]*?]|^)\$autoload\['(?:model|libraries)'\][\s]*?=[\s]*?array[\s]*?)(.*?\))"
# r                             Escape python reg ex string
# (?:                           Start a non capturing match
# (?:                           Start a inner non capturing match
# [^\|[\s]*?]|^)                match a string that does NOT start with a pipe  followed by 0 or more white space (ie, the CI comments)
# \$autoload\['                 followed by the string $autoload[' 
# (?:model|libraries)           start non capturing match for models or libraries
# '\][\s]*?=[\s]*?array[\s]*?   match the string  '] = array with 0 or more spaces between the =
# )                             close the no capturing match
# (.*?\)                        capture everything up to the next closing bracket )
# )                             close non capturing match

# matches text between single or double quotes
CLASS_LIST_PATTERN = '\"(.+?)\"|\'(.+?)\''

COMMENT_PATTERN = """/**
 * @var {class}
 */            
var ${var};    
"""


# If this pattern exists in a class (hook / library)
# Then write out match(1) as type CI_Controller in the current class
# and add any loads made via match(1) to it.
CI_INSTANCE_PATTERN = r'^[\s]*?[^//,*][\s]*?\$(.*?)[\s]*?\=\&[\s]*?get_instance'

files_created = 0

# Loggin constants
FAIL = -1
NORM = 0    
WARN = 1
INFO = 2
TITLE = 3



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--codeigniter', default='../www', help='path to codeigniter project relative to codecomplete')
    args = parser.parse_args()
    

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
    
    
    


          
# Finds any auto loaded classes that need to be added to all output classes
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
  
    #Get the auto loads that are applied to every class        
    global auto_loads  
   
    class_header = ''
    class_footer = '\n'+CLASS_CLOSE_BRACKET
    class_name = getFileName(filepath) # Assume class name is same as file..
    
    # if the user has loaded an instance of CI into a local var, it will be saved here
    ci_field = ''
    
    # dictionary of members indexed by scope / parent class
    classes = {}
    
    #Open out files (and create the out file)
    in_file = open(filepath, 'r+')
        
    with in_file as f:
        data = mmap.mmap(f.fileno(), 0)
        
        #Get the main Class definition
        mo = re.search(CLASS_PATTERN, data, re.M)
        if mo:
            class_header = mo.group(0)
            #Check if we need to add the php tag, and start the class..
            if CLASS_OPEN_BRACKET not in class_header:
                class_header = join([class_header,' ',CLASS_OPEN_BRACKET])
			
            if PHP_TAG not in class_header:
                class_header = join([PHP_TAG,'\n',class_header])

        # Check if an instance of CI is used, $CI =$ get_instance(), for example.
        mo = re.search(CI_INSTANCE_PATTERN, data, re.M )
        if mo:
            ci_instance = mo.group(1)
            #remove this-> from the instance name
            ci_instance = getPropertyName(ci_instance)
            #create a custom type for this class that we can use locally
            ci_type = join([upcase_first_letter(ci_instance), "_",  class_name])
            ci_comment = buildCommentString(ci_instance, ci_type)
            if ('this' not in classes):
                classes['this'] = ''
            # Save the CI property to the main scope  
            classes['this'] = join([classes['this'], '\n', ci_comment])
            
        
        # Find any loads for Models, Libraries etc
        it1 = re.finditer(LOAD_PATTERN, data, re.M | re.I | re.S)
        for mo1 in it1:
            #Either 'this' or a property name that holds an instance of CI
            scope = mo1.group(1)
            members = mo1.group(2)
            # This converts 'this->CI' into CI, or leave 'this' alone.
            # The result is an owner as either 'this' or a property name
            scope = getPropertyName(scope)
            it2 = re.finditer(CLASS_LIST_PATTERN,  members)
            
            for mo2 in it2:
                # ensure we have a key in the dict..
                if (scope not in classes):
                    classes[scope] = ''
    
                #write the property to the appropriate scope key
                classes[scope] = join([classes[scope], '\n', getComment(mo2.group(0))])

    
    
    #Now create the classes.  We have two approaches:
    # If a load was made using $this->load, then we write those types out to the main class
    # If a load was made via another property that was created with =& get_instance() (as in A Hook or Library class)
    # then we write the property that was created into the main class, and create a new class for the property which
    # holds all the types loaded
    #
    # This ensures both $this->my-model  will autocomplete when in an instance of CI_Controller.
    # As well as $this->CI->my_model when referencing the CI_Controller
    if (('this' in classes) or (auto_loads != '')):
        out_file = cloneFile(filepath)
        #write out the new code complete class
        out_file.write(class_header)
        out_file.write("\n//Class fields")
        out_file.write(classes['this'])
       
       # If we have auto loads, write them out
        if( auto_loads != '' ):
            out_file.write("\n//Auto loaded fields")
            current_auto_load = auto_loads
            #If the current class is in the auto load, remove it so we dont get cyclical reference
            if( class_name in current_auto_load ):
                current_auto_load = current_auto_load.replace("@var " + class_name, '', re.I)
                current_auto_load = current_auto_load.replace("var $" + class_name.lower() + ";", '', re.I)
            
            out_file.write(current_auto_load)
        
       
        # if we have a custom instance of CI, write it out
        if( ci_field !='' ):
            out_file.write("\n//CI References\n")
            out_file.write(ci_field);
        
        # Close the class
        out_file.write(class_footer)
         
        # write out remaining local classes (local instance of CI for example)
        for k, v in classes.iteritems():
            if(k != 'this'):
                out_file.write('\n\n//Create local class for instance of CI that has been loaded \n')
                out_file.write( join(['class ', k, '_', class_name, ' extends CI_Controller ', CLASS_OPEN_BRACKET]))
                out_file.write(v)
                out_file.write(class_footer)
        
        out_file.close()
        
    in_file.close()
    

# Returns the file name (file name) from a file path
def getFileName(filepath):
    file = os.path.split(filepath)[-1]
    file_name = file.replace('.php','')
    return file_name    
    
    
# Strips out this->, or this -> from the property path     
def getPropertyName(propertyPath):
    return re.sub(r'this[.*]?->','',propertyPath)

    
def cloneFile(filepath):
    #Resolve path to new code-complete file
    cc_filepath = filepath.replace(ci_dir, SELF_DIR)
    makeDir(cc_filepath)
    msg( 'Creating: ' + cc_filepath )
    out_file = open(cc_filepath, 'w+')
    global files_created
    files_created+=1
    return out_file
        
# Makes a writable dir path based on the path passed in
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
    

# Returns the comment structure for the classpath passed in
def getComment(classpath):
    
    #clean the quotes out - cant get the regex above to do this for some reason.
    classpath =  classpath.replace('\"','').replace('\'','')
    #Split on path delimiters, and take the last element, the class name
    classpath = classpath.split('/')
    classname = classpath[-1]
    
    return buildCommentString(classname)

# Builds the comment string for  classname and type
def buildCommentString(classname, type=None):
    if(type==None):
        comment = COMMENT_PATTERN.replace("{class}", upcase_first_letter(classname))
    else:
        comment = COMMENT_PATTERN.replace("{class}", type)
    
    comment = comment.replace("{var}", classname)
    return comment

    
def upcase_first_letter(s):
    return s[0].upper() + s[1:]
    
def join( array ):
    return ''.join(array)

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
        

	
	
# go	
if __name__ == '__main__':
	main()




