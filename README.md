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

This will create a property called *$my_model* of type *My_model* for the file `models/my_model.php`

The script will generate auto complete files for all your models, controllers, libraries, helpers, hooks and custom core files. 

It supports HMVC set ups as well,  so any classes under a *modules* package will also be detected. 

It has been tested with the following strucutres

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

$this->CI =& get_instance();
$this->CI->load->model('my_package/my_model') ;

$this->any_var_name =& get_instance();
$this->any_var_name->load->model('my_package/my_model') ;

$CI =& get_instance();
$CI->load->model('my_package/my_model') ;
```


##Installation##
This assumes you have a git repo for your codeigniter project that contains a `www` directory.  

1) Clone the codecomplete repo into your project, the best approach is to place it at the same level 
as you CI site, so use `git submodule` if you are already in a git repo:

```bash
git submodule add https://github.com/mattbryson/Codeigniter_Code_Complete.git codecomplete
````
(Removing submodules can be a bit tricky, so you could just cheat and have a git repo nested in your current git repo)

2) Then run the script:

```bash
python codecomplete/build.py -c ../www
```
Where `codecomplete` is the this repo and `-c` is the path to you codeigniter site relative to the `codecomplete` directory.


3) Next add the directory to you Eclipse PHP Build path.

* File > Properties > PHP Buildpath
* Click on the 'External Directories' tab
* Click the 'add' button to the right and browse to the `codecomplete` directory.


Now you will have code-complete in you custom Codeigniter classes.

#Workflow#
Add a copy of `codecomplete` into each codeigniter project you work on, at the same level as your `www` directory.
Each time you add a new reference to a model, library or helper in one of you classes you must re build the `codecomplete` files.
It only takes a second to run, and saves you a lot of time in the long run. You will need to save the class to get Eclipse to re check the class paths.

#Disclaimer#
**This script has been tested however, USE AT YOUR OWN RISK.**
The script will delete the directories it creates when run for a second time.
The script is provided “as is” without any warranty of any kind and I disclaim any and all liability regarding any use of the scripts.
