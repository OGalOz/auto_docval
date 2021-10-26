"""
The goal of this file is to auto document
a python file.
It looks for every function; Considers the
inputs. If the inputs to the function are
all in the varspec.json sheet, then it
simply adds the classic documentation.
If the inputs aren't, then it raises
an error and states which input
wasn't included.
It also looks for a custom return string
right above each function definition.
This string looks like '# rets X Y ',
where X and Y would be variable names.
Normally this should only return one
thing.
If there is already a docstring under
the function, then it appends the new documentation
above it, within the triple quotation - 
However, there must be a way to symbolize
that the documentation has already been
added and to not duplicate it every time
the program is run.
"""

import os
import re
import logging
import json
import sys
import copy
from validate_types import import_all_types




# rets funcN2vars
def get_func_name_to_vars_from_file(python_file_fp):
    """
    *DOCDONE
    Args:
        python_file_fp (string): Path to python file to document.
            Restriction: is_file=1
    Returns:
        funcN2vars (dict): Dict mapping function name to a dict holding variables
            func_name -> argsNret_d
                func_name (string): Name of function, no spaces and doesn't start with number
                argsNret_d (dict): Dict mapping 'args' and 'returns' to a list of variables in def
                        Args -> variables_list (list<var>), list of variables normally returned.
                        Returns -> variables_list (list<var>), list of variables normally returned.
    """
    func_name_to_locs = get_function_names_starts_and_ends(python_file_fp)
    #print(function_names_to_starts_and_ends)
    funcN2vars = get_func_name_to_variables(func_name_to_locs, 
                                            python_file_fp)
    return funcN2vars

# rets funcN2vars2docstr
def create_documentation_args_returns_str(funcN2vars,
                                           type_spec_d,
                                           types_cfg_json_fp):
    """
    *DOCDONE
    Args:
        funcN2vars (dict): Dict mapping function name to a dict holding variables
            func_name -> argsNret_d
                func_name (string): Name of function, no spaces and doesn't start with number
                argsNret_d (dict): Dict mapping 'args' and 'returns' to a list of variables in def
                        Args -> variables_list (list<var>), list of variables normally returned.
                        Returns -> variables_list (list<var>), list of variables normally returned.
        type_spec_d (dict): The dict that holds the information about all the variables.
            var -> spec_d
                var (string): Name of a variable
                spec_d (dict): The dict that holds the information about a single variable.
                        subtype -> string (string), standard python string
                        desc -> string (string), standard python string
        types_cfg_json_fp (string): Path to all type spec file.
            Restriction: is_file=1
    Returns:
        funcN2vars2docstr (dict): Dict mapping function name to variables mapped to doc strings.
            func_name -> var2docstr_d
                func_name (string): Name of function, no spaces and doesn't start with number
                var2docstr_d (dict): Dict mapping variables to their docstrings
                    var -> docstrs_major_l
                        var (string): Name of a variable
                        docstrs_major_l (list<docstr_l>): Outer list of layers of docstrings in sublists.
    """
    """
    """

    funcN2vars2docstr_l = {}
    for func_name, argsNret_d in funcN2vars.items():
        exchange_d = {}
        for x in ["Args", "Returns"]:
            func_vars = argsNret_d[x]
            var2docstr_l = {}
            for var in func_vars:
                if var not in type_spec_d:
                    raise Exception(f"Variable {var} from function {func_name}, " + \
                                    f"group {x}, not in type_spec_d from " + \
                                    f"file {types_cfg_json_fp}")
                spec_d = type_spec_d[var]
                if "subtype" not in spec_d:
                    raise Exception(f"Variable {var} from function {func_name} " + \
                                    f" does not have key 'subtype'.")
                if "desc" not in spec_d:
                    raise Exception(f"Variable {var} from function {func_name} " + \
                                    f" does not have key 'desc'.")
                docstrs_l = prepare_docstrs_l(var, type_spec_d, 1)
                var2docstr_l[var] = docstrs_l
            exchange_d[x] = var2docstr_l

        funcN2vars2docstr_l[func_name] = exchange_d 
    return funcN2vars2docstr_l 





# rets crt_var_list 
def prepare_docstrs_l(var, type_spec_d, current_num_layer, 
                      max_num_layers=4, dict_key=None):
    """
    *DOCDONE
    Args:
        var (string): Name of a variable
        type_spec_d (dict): The dict that holds the information about all the variables.
            var -> spec_d
                var (string): Name of a variable
                spec_d (dict): The dict that holds the information about a single variable.
                        subtype -> string (string), standard python string
                        desc -> string (string), standard python string
        current_num_layer (int): Keeping track of the layer in which we are operating for doc strings
        max_num_layers (int): Upper limit to the layers in which we are operating for doc strings
        dict_key (string): A key for a dict to add to doc str
    Returns:
        crt_var_list (pass): Non-fixed data structure.
    """
    """
    Description:
        This recursive function returns either a string or a list,
            depending on the layer number
        # Note, if max_num_layers = -1, then there is no limit to layers.
        If dict_key is not None, then this is a part of a dict
    """
    logging.debug(f"Preparing docstrings list for variable {var}. Layer: {current_num_layer}.")

    # "" represents don't print another doc string
    if max_num_layers != -1 and current_num_layer >= max_num_layers:
        return ""
    #if var in ["string", "int", "float", "skip", "bool", "None"]:
    #    return ""

    if var not in type_spec_d:
        raise Exception(f"var {var} missing from type_spec_d")
    crt_spec_d = type_spec_d[var]
    
    st = crt_spec_d["subtype"]
    crt_var_list = []
    if dict_key is not None:
         this_var_doc_str = f"{dict_key} -> {var}"
         crt_var_list.append(this_var_doc_str)
    this_var_doc_str = f"{var} ({st}): {crt_spec_d['desc']}"
    crt_var_list.append(this_var_doc_str)
    
    if st in ["string", "int", "float", "skip", "bool"]:
        if "restrictions" in crt_spec_d:
            r_d = crt_spec_d["restrictions"]
            layer_2 = []
            for k, v in r_d.items():
                layer_2.append(f"Restriction: {k}={v}")
            crt_var_list.append(layer_2)
        return crt_var_list
    elif st == "dict":
        layer_2 = []
        if "dict_keys" in crt_spec_d:
            for k, v in crt_spec_d["dict_keys"].items():
                if not check_var_against_type_spec_d(v, type_spec_d):
                    raise Exception(f"Dict keys value {v} not in type_spec_d.")
                if "list" not in v:
                    layer_2.append(prepare_docstrs_l(v, type_spec_d, current_num_layer + 1, dict_key=k))
                else:
                    list_subtype = (v.split("<")[1]).split(">")[0]
                    layer_2.append(prepare_docstrs_l(list_subtype, type_spec_d, current_num_layer + 1, dict_key=k))

        elif "dict_spec" in crt_spec_d:
            k = list(crt_spec_d["dict_spec"].keys())[0]
            v = crt_spec_d["dict_spec"][k]
            if not check_var_against_type_spec_d(k, type_spec_d):
                raise Exception(f"Dict spec key {k} not in type_spec_d.")
            if not check_var_against_type_spec_d(v, type_spec_d):
                raise Exception(f"Dict spec value {v} not in type_spec_d.")
            layer_2.append(f"{k} -> {v}")
            layer_2.append(prepare_docstrs_l(k, type_spec_d, current_num_layer+1))
            if "list" not in v:
                layer_2.append(prepare_docstrs_l(v, type_spec_d, current_num_layer + 1))
            else:
                list_subtype = (v.split("<")[1]).split(">")[0]
                layer_2.append(prepare_docstrs_l(list_subtype, type_spec_d, current_num_layer + 1))
        elif "unknown" in crt_spec_d:
            layer_2.append(f"Unknown keys (variable input).")
        else:
            raise Exception("No recognized keys in dict spec_d. "  + \
                            "Must be one of 'dict_keys', 'dict_spec', 'unknown'." + \
                            " Existing keys " + ', '.join(crt_spec_d.keys()))
        crt_var_list.append(layer_2)
    elif "list" in st:
        layer_2 = []
        list_subtype = (st.split("<")[1]).split(">")[0]
        if not check_var_against_type_spec_d(list_subtype, type_spec_d):
            raise Exception(f"List subtype {list_subtype} not in type_spec_d.")
        layer_2.append(prepare_docstrs_l(list_subtype, type_spec_d, current_num_layer + 1))
        crt_var_list.append(layer_2)

    logging.debug("For variable {var}, docstrings list is: ")
    logging.debug(crt_var_list)
    return crt_var_list


def check_var_against_type_spec_d(var, type_spec_d):
    """
    *DOCDONE
    Args:
        var (string): Name of a variable
        type_spec_d (dict): The dict that holds the information about all the variables.
            var -> spec_d
                var (string): Name of a variable
                spec_d (dict): The dict that holds the information about a single variable.
                        subtype -> string (string), standard python string
                        desc -> string (string), standard python string
    Returns:
    """
    # Returns True if good, False if bad
    if "list" not in var:
        if var not in type_spec_d:
            return False 
        else:
            return True
    else:
        var = (var.split("<")[1]).split(">")[0]
        if var not in type_spec_d:
            return False 
        else:
            return True




# rets funcN2vars 
def get_func_name_to_variables(func_name_to_locs, python_file_fp):
    """
    *DOCDONE
    Args:
        func_name_to_locs (dict): Dict mapping function names to definition's start and end line within file
            func_name -> start_end_d
                func_name (string): Name of function, no spaces and doesn't start with number
                start_end_d (dict): Dict mapping function names to definition's start and end line within file
                        func_start -> int (int), standard python int
                        func_end -> int (int), standard python int
        python_file_fp (string): Path to python file to document.
            Restriction: is_file=1
    Returns:
        funcN2vars (dict): Dict mapping function name to a dict holding variables
            func_name -> argsNret_d
                func_name (string): Name of function, no spaces and doesn't start with number
                argsNret_d (dict): Dict mapping 'args' and 'returns' to a list of variables in def
                        Args -> variables_list (list<var>), list of variables normally returned.
                        Returns -> variables_list (list<var>), list of variables normally returned.
    """
    """
    Description:
        
    """
    
    file_lines = open(python_file_fp).read().split("\n")
    funcN2vars = {}
    for func_name in func_name_to_locs.keys():
        f_strt = func_name_to_locs[func_name]["func_start"]
        f_end =  func_name_to_locs[func_name]["func_end"]
        func_ret_str = file_lines[f_strt - 1]
        func_def_str = " ".join(file_lines[f_strt:f_end + 1])
        # Removing multiple spaces
        func_def_str = " ".join(func_def_str.split())
        # func_vars is a list of strings, each a variable
        func_vars = get_function_variables_from_func_string(func_def_str)
        argsNret_d = {}
        if '' in func_vars:
            func_vars.remove('')
        if len(func_vars) > 0:
            argsNret_d["Args"] = func_vars
            funcN2vars[func_name] = argsNret_d  

        ret_vars = get_function_return_variables(func_ret_str)
        if '' in ret_vars:
            ret_vars.remove('')
        if len(func_vars) > 0:
            argsNret_d["Returns"] = ret_vars 
            funcN2vars[func_name] = argsNret_d  

    return funcN2vars

# rets variables_list
def get_function_return_variables(func_ret_str):
    """
    *DOCDONE
    Args:
        func_ret_str (string): String defining what a function returns within this system.
    Returns:
        variables_list (list<var>): list of variables normally returned.
                var (string): Name of a variable
    """
    """
    Desc:
        func_ret_str has to have a specific format:
        must look like '# rets {X}'.
    """
    #HERE
    if not func_ret_str[:7] == "# rets ":
        return []
    else:
        real_rets_str = func_ret_str[7:]
        print(real_rets_str)
        split_rets_str = real_rets_str.split(" ")
        return split_rets_str


# rets variables_list 
def get_function_variables_from_func_string(func_string):
    """
    *DOCDONE
    Args:
        func_string (string): multiline string of function
    Returns:
        variables_list (list<var>): list of variables normally returned.
                var (string): Name of a variable
    """
    variables_list = []
    variables_str = "".join(func_string.split("(")[1:])
    variables_str = "".join(variables_str.split(")")[:-1])
    init_variables_list = variables_str.split(", ")
    for v in init_variables_list:
        if '=' in v:
            variables_list.append(v.split("=")[0])
        else:
            variables_list.append(v.strip())

    return variables_list


# rets func_name_to_locs
def get_function_names_starts_and_ends(python_file_fp):
    """
    *DOCDONE
    Args:
        python_file_fp (string): Path to python file to document.
            Restriction: is_file=1
    Returns:
        func_name_to_locs (dict): Dict mapping function names to definition's start and end line within file
            func_name -> start_end_d
                func_name (string): Name of function, no spaces and doesn't start with number
                start_end_d (dict): Dict mapping function names to definition's start and end line within file
                        func_start -> int (int), standard python int
                        func_end -> int (int), standard python int
    """

    file_lines = open(python_file_fp).read().split("\n")
    file_len = len(file_lines)
    func_name_to_locs = {}

    for i in range(file_len):
        c_line = file_lines[i]
        if c_line[0:4] == "def ":
            function_name = re.findall(r"^\w+", c_line[4:])[0]
            logging.debug(f"found func; name: {function_name} start at row {i}.")
            func_start = i
            j = 0
            while i + j < file_len:
                next_line = file_lines[i + j]
                # Two seperate regex searches, which one works?
                m = re.search(r'\):[\s]*$', next_line)
                if not m:
                    j += 1
                else:
                    if m:
                        logging.debug("m found match at line " + str(i+j))
                    func_end = i + j
                    if function_name in func_name_to_locs:
                        raise Exception("Duplicate function name: " + function_name)
                    func_name_to_locs[function_name] = {'func_start': func_start,
                                                       'func_end': func_end}
                    break
                if i + j == file_len:
                    print(func_name_to_locs)
                    raise Exception("File parsing error, reached EOF")

    return func_name_to_locs


# rets None 
def add_docstrings_to_file(python_file_fp, funcN2vars2docstr): 
    """
    *DOCDONE
    Args:
        python_file_fp (string): Path to python file to document.
            Restriction: is_file=1
        funcN2vars2docstr (dict): Dict mapping function name to variables mapped to doc strings.
            func_name -> var2docstr_d
                func_name (string): Name of function, no spaces and doesn't start with number
                var2docstr_d (dict): Dict mapping variables to their docstrings
                    var -> docstrs_major_l
                        var (string): Name of a variable
                        docstrs_major_l (list<docstr_l>): Outer list of layers of docstrings in sublists.
    Returns:
        None (None): None type
    """
    """
    Desc:
        We break out of adding documentation if the flag
        '*DOCDONE' is the first line after the start of
        the function's documentation comment. This way,
        you can update the documentation if the flag
        isn't there.
    """
    #HERE
    
    op_fp = os.path.join(os.getcwd(), "doct_" + os.path.basename(python_file_fp))
    if os.path.isfile(op_fp):
        raise Exception("Output file exists at " + op_fp)

    func_name_to_locs = get_function_names_starts_and_ends(python_file_fp)

    end_to_func_name = {func_name_to_locs[x]["func_end"]:x for x in func_name_to_locs.keys()}

    file_lines = open(python_file_fp).read().split("\n")

    op_file_str_lines = []
    spacer = " "*4
    for i in range(len(file_lines)):
        op_file_str_lines.append(file_lines[i])
        if i in end_to_func_name:
            # Checking if documentation is needed
            next_line = file_lines[i+1]
            if '"""' in next_line:
                if '*DOCDONE' in file_lines[i+2]:
                    continue
            func_name = end_to_func_name[i]
            if func_name not in funcN2vars2docstr:
                continue 
            vars_d = funcN2vars2docstr[func_name]
            op_file_str_lines.append(spacer + '"""')
            op_file_str_lines.append(spacer + '*DOCDONE')
            op_file_str_lines.append(spacer + "Args:")
            args_d = vars_d["Args"]
            for var, var_docstrs_l in args_d.items():
                logging.debug(f"Working on var {var}.")
                generate_docstr_from_docstr_l(var_docstrs_l, spacer,
                                                2, op_file_str_lines)
            op_file_str_lines.append(spacer + "Returns:")
            rets_d = vars_d["Returns"]
            for var, var_docstrs_l in rets_d.items():
                logging.debug(f"Working on var {var}.")
                generate_docstr_from_docstr_l(var_docstrs_l, spacer,
                                                2, op_file_str_lines)

            op_file_str_lines.append(spacer + '"""')
            #logging.info(f"Function {func_name} found at line {i}.")

    with open(op_fp, "w") as g:
        g.write("\n".join(op_file_str_lines))

    logging.info(f"Wrote output file to {op_fp}")

    return None


def generate_docstr_from_docstr_l(docstr_l, spacer, num_depth, op_file_str_lines):
    """
    *DOCDONE
    Args:
        docstr_l (pass): Passing type for infinite recursion reasons, this is a list with subtype list or string.
        spacer (string): Spaces which mark indentation level for doc strings
        num_depth (int): Multiplier for spacers to show proper depth of variable
        op_file_str_lines (list<string>): Output file in format list of strings, one string per line, no new-line symbol.
                string (string): standard python string
    Returns:
    """
    # docstr_l is a list in which each item is either a string or a docstring list
    # Every time this runs, it adds a line to the op_file_str_lines list.
    if num_depth >= 10:
        print(docstr_l)
        with open("ErrorFile.txt", "w") as g:
            g.write('\n'.join(op_file_str_lines))
        raise Exception("Docstring depth exceeds 10 - possible loop issue.")
    
    for x in docstr_l:
        if isinstance(x, str):
            if x != "":
                op_file_str_lines.append(spacer*num_depth + x)
        elif isinstance(x, list):
            generate_docstr_from_docstr_l(x, spacer, num_depth + 1, op_file_str_lines)




        
def test_1(types_cfg_json_fp, python_file_fp):
    """
    *DOCDONE
    Args:
        types_cfg_json_fp (string): Path to all type spec file.
            Restriction: is_file=1
        python_file_fp (string): Path to python file to document.
            Restriction: is_file=1
    Returns:
    """

    type_spec_d = import_all_types(types_cfg_json_fp)



def test_3(types_cfg_json_fp, python_file_fp):
    """
    *DOCDONE
    Args:
        types_cfg_json_fp (string): Path to all type spec file.
            Restriction: is_file=1
        python_file_fp (string): Path to python file to document.
            Restriction: is_file=1
    Returns:
    """
    type_spec_d = import_all_types(types_cfg_json_fp)
    funcN2vars = get_func_name_to_vars_from_file(python_file_fp)
    funcN2vars2docstr = create_documentation_args_returns_str(funcN2vars,
                                                              type_spec_d,
                                                              types_cfg_json_fp)

    add_docstrings_to_file(python_file_fp, funcN2vars2docstr)
    #print(func_names_to_doc_strings)




def test_2(python_file_fp):
    """
    *DOCDONE
    Args:
        python_file_fp (string): Path to python file to document.
            Restriction: is_file=1
    Returns:
    """
    get_functions_info_from_file(python_file_fp)
    


def main():
    args = sys.argv
    logging.basicConfig(level=logging.DEBUG)
    help_str = "python3 document_with_types.py types_cfg_json_fp python_file_fp 1"
    help_str += "\nOR\n" 
    help_str += "python3 document_with_types.py python_file_fp 2"
    help_str += "\nOR\n" 
    help_str += "python3 document_with_types.py types_cfg_json_fp python_file_fp 3"

    if args[-1] not in ["1", "2", "3"]:
        print("Not running.")
        print(help_str)
        sys.exit(1)
    elif args[-1] == "1":
        types_cfg_json_fp = args[1]
        python_file_fp = args[2]
        test_1(types_cfg_json_fp, python_file_fp)
        sys.exit(0)
    elif args[-1] == "2":
        python_file_fp = args[1]
        test_2(python_file_fp)
        sys.exit(0)
    elif args[-1] == "3":
        types_cfg_json_fp = args[1]
        python_file_fp = args[2]
        test_3(types_cfg_json_fp, python_file_fp)
        sys.exit(0)
    else:
        print(help_str)
        sys.exit(1)

if __name__ == "__main__":
    main()
