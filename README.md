Codeigniter Code-Complete for custom classes
============================================

Generates a reflection of a CodeIgniter project, and writes comments defining property types to enable auto code completion in IDEs such as eclipse.

##Installation##
1) Clone the repo to you computer, and then run the following command line:

```bash
python assets/codecomplete/build.py -c ../../www
```
Where -c is the path to you codeigniter site relative to the CI_CodeComplete directory.


2) Next add the directory to you Eclipse PHP Build path.

* File > Properties > PHP Buildpath
* Click on the 'External Directories' tab
* Click the 'add' button to the right and browse to the CI_CodeComplete directory.


Now you will have code-complete in you custom codeigiter classes.

#Workflow#
You must re build the code complete files every time you reference a new model, library or helper in one of you classes.
