Codeigniter Code Complete
=========================

Generates a reflection of a CodeIgniter project, and writes comments defining property types to enable auto code completion in IDEs such as eclipse.

Clone the repo to you computer, and then run the following command line:

python assets/codecomplete/build.py -c ../../www

Where -c is the path to you codeigniter site relative to the CI_CodeComplete directory.


Next add the directory to you Eclipse PHP Build path.

File > Properties > PHP Buildpath

Click on the 'External Directories' tab
Click the 'add' button to the right and browse to the CI_CodeComplete directory.


Now you will have codecomplet in you custom codeigiter classes.

You must re build the code complete files every time you add reference a new model, library or helper.