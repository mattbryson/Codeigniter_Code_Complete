Codeigniter Code-Complete for custom classes
============================================

Generates a reflection of a CodeIgniter project, and writes comments defining property types to enable auto code completion in IDEs such as eclipse.

##Installation##
1) Clone the repo to you computer, and then run the following command line:

```bash
python codecomplete/build.py -c ../www
```
Where codecomplete is the codecomplete repo and -c is the path to you codeigniter site relative to the codecomplete directory.

If you want to add this to an existing repo, consider using a git-submodule.


2) Next add the directory to you Eclipse PHP Build path.

* File > Properties > PHP Buildpath
* Click on the 'External Directories' tab
* Click the 'add' button to the right and browse to the CI_CodeComplete directory.


Now you will have code-complete in you custom codeigiter classes.

#Workflow#
I would add a copy of codecomplete into each codeigniter project, at the same level as you www directory.
Each time you add a new reference a new model, library or helper in one of you classes you must run build the codecomplete files.
However, it only takes a second to run, and saves you a lot of time in the long run.

#Disclaimer#
** This script has been tested however, USE AT YOUR OWN RISK. **
The script will delete the directories it creates when run for a second time.
The script is provided “as is” without any warranty of any kind and I disclaim any and all liability regarding any use of the scripts.
