Codeigniter Code-Complete for custom classes
============================================

Creates autocomplete comments for user classes as well as the CodeIgniter core without modifying your code.

Generates a reflection of a CodeIgniter project, and writes comments defining property types to enable auto code completion in IDEs such as eclipse.
The code is class specific, so only the models and libraries referenced in your class will be available in the code complete.

##Format##
The script makes the assumption that your class properties follow the standard CI naming conventions.  For example.. 
```php
$this->load->model('my_model') ;
```

THis will create a property called *$my_model* of type *My_model*

The script will generate auto complete files for all your models, controllers,  libraries,  helpers and custom core files. 

It supports HMVC set ups as well,  so any classes under a *modules* package will also be detected. 

It has been tested with the following layouts

```php
$this->load->model('my_model') ;
$this->load->model('my_model') ;
$this -> load -> model ( 'my_model' ) ;
$this->load->model(array('my_model', 'my_other_model') ) ;
$this->load->model(
array(
'my_model', 
'my_other_model'
) ) ;
$this->load->model('my_package/my_model') ;
```
##Installation##
1) Clone the repo to you computer, and then run the following command line:

```bash
python CI_CodeComplete/build.py -c ../www
```
Where CI_CodeComplete is the CI_CodeComplete repo and -c is the path to you codeigniter site relative to the CI_CodeComplete directory.

If you want to add this to an existing repo, consider using a git-submodule.


2) Next add the directory to you Eclipse PHP Build path.

* File > Properties > PHP Buildpath
* Click on the 'External Directories' tab
* Click the 'add' button to the right and browse to the CI_CodeComplete directory.


Now you will have code-complete in you custom Codeigniter classes.

#Workflow#
Add a copy of CI_CodeComplete into each codeigniter project you work on, at the same level as your www directory.
Each time you add a new reference a new model, library or helper in one of you classes you must re build the CI_CodeComplete files.
It only takes a second to run, and saves you a lot of time in the long run.

#Disclaimer#
**This script has been tested however, USE AT YOUR OWN RISK.**
The script will delete the directories it creates when run for a second time.
The script is provided “as is” without any warranty of any kind and I disclaim any and all liability regarding any use of the scripts.
