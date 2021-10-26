# auto_docval

In order to add documentation to your python
file, run the following command:
`python3 document_with_types.py variable_spec.json python_file_to_document.py 1`
Now note that the file with the most restrictions is the 'variable_spec.json' file.
Notice that it doesn't need to be named 'variable_spec.json', it only needs to be
a JSON file that follows these rules:
The entire file is a dict with the key "types" in it.
This key "types" points to a list of specification dicts.
Each specification dict labels a single variable, and has the following rules:
A. it must have the keys "name", "subtype", and "desc".
B. It can optionally have the keys "dict_keys", "dict_spec", "restrictions", and "optional_keys",
    depending on the subtype of the variable. If the variable is a dict, you must choose for
    it to have one of "dict_keys" or "dict_spec". If you choose "dict_keys", then
    you can also optionally have the key "optional_keys", but if you choose "dict_spec"
    you cannot. "restrictions" is a key that can only be used if the "subtype" is
    one of ["string", "int", "float", "skip", "bool"]. 

The options for subtypes before listing any variables are:
    dict, float, string, bool, int , pass, None.
Once you've created variables, then you can use those variables
as subtypes further down the list of types. The program will 
raise an Error if you use a variable that is created further
down the list as a subtype (aside from the basic atomic variables
listed above). As an example variable_spec.json file, consider
the file 'doc_val_varspec.json' in this directory. It was used
to document the file 'document_with_types'.








Just as you would have with python, at first you would need to build the atomic types,
those that have subtypes from "string",
