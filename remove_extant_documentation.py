"""
The goal of this file is to 
remove the automatic documentation
of a file that already has documentation.

It looks for every function; Considers the
doc-strings beneath the function definition.
If *DOCDONE is there - then we remove that
documentation up until the next triple quotation marks.
Quotation marks will normally be doubled: "*3


Functions necessary:
    1st: Convert python file into a list of strings
        separated by new line symbols.
    2nd: Find the function definitions with 
        triple quotes underneath and then *DOCDONE
        underneath that.
    3rd: Find the end of that documentation and remove
        those quotations.
    4th: Print out new file without documentation to
        a location other than the original python file
        (don't overwrite) - note where to the console output.


"""

import os
import re
import logging
import json
import sys
import copy
from validate_types import import_all_types
from document_with_types import get_function_names_starts_and_ends, ostop


def remove_autodocs_from_file(python_file_fp):
    
    func_name_to_locs = get_function_names_starts_and_ends(python_file_fp)
    func_to_autodocd = check_if_funcs_autodocd(python_file_fp, func_name_to_locs) 
    print(func_to_autodocd)
    
    #ostop("39")
    return None

# rets func_to_autodocd
def check_if_funcs_autodocd(python_file_fp, func_name_to_locs):

    with open(python_file_fp, 'r') as f:
        split_file = f.read().split('\n')

    func_to_autodocd = {}
    for func_name in func_name_to_locs.keys():
        start_end_d = func_name_to_locs[func_name]
        func_end = start_end_d["func_end"] 
        if '"""' in split_file[func_end + 1] and '*DOCDONE' in split_file[func_end + 2]:
            end_doc = 1
            doc_end_found = False
            while not doc_end_found:
                if '"""' in split_file[func_end + 2 + end_doc]:
                    doc_end_found = True
                else:
                    end_doc += 1
            func_to_autodocd[func_name] = {"doc_start": func_end + 1,
                                           "doc_end": func_end + 2 + end_doc}

    return func_to_autodocd




def main():
    help_str = "python3 remove_extant_documentation.py py_file 1"
    args = sys.argv
    if args[-1] != "1":
        print(help_str)
        sys.exit(1)
    else:
        python_file_fp = args[1]
        if not os.path.exists(python_file_fp):
            raise Exception(f"File not found at location {python_file_fp}")
        remove_autodocs_from_file(python_file_fp)

if __name__ == "__main__":
    main()
