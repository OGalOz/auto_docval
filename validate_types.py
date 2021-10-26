


#import os
import re
import logging
import json
import sys
import copy


def check_cfg_d(cfg_d, type_spec_d):
    """
    *DOCDONE
    Args:
        cfg_d (pass): Non-fixed data structure.
        type_spec_d (dict): The dict that holds the information about all the variables.
        -maps var -> spec_d
            var (string): Name of a variable
            spec_d (dict): The dict that holds the information about a single variable.
            -keys:
                'subtype' -> subtype (string), String describing what the type of a variable is.
                'desc' -> desc (string), String describing a variable's meaning.
            -optional keys:
                '[dict_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[optional_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[dict_spec]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[restrictions]' -> restrictions_d (dict), The dict that holds restrictions for various objects.
                -optional keys:
                    '[regex]' -> string (string), standard python string
                    '[less_than]' -> float (float), standard python float
                    '[greater_than]' -> float (float), standard python float
                    '[decimal_max]' -> int (int), standard python int
    """
    keys_list = list(cfg_d.keys())
    for key in keys_list:
        check_object_against_types(key, cfg_d[key], type_spec_d)

def check_object_against_types(obj_name, obj, type_spec_d):
    """
    *DOCDONE
    Args:
        obj_name (var): Name of a variable
            ( var (string): Name of a variable )
        obj (pass): Unknown Object.
        type_spec_d (dict): The dict that holds the information about all the variables.
        -maps var -> spec_d
            var (string): Name of a variable
            spec_d (dict): The dict that holds the information about a single variable.
            -keys:
                'subtype' -> subtype (string), String describing what the type of a variable is.
                'desc' -> desc (string), String describing a variable's meaning.
            -optional keys:
                '[dict_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[optional_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[dict_spec]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[restrictions]' -> restrictions_d (dict), The dict that holds restrictions for various objects.
                -optional keys:
                    '[regex]' -> string (string), standard python string
                    '[less_than]' -> float (float), standard python float
                    '[greater_than]' -> float (float), standard python float
                    '[decimal_max]' -> int (int), standard python int
    """
    logging.debug(f"Checking object {obj_name} against type_spec_d")
    if obj_name not in type_spec_d:
        raise Exception(f"Object name {obj_name} not found in type_spec_d")
    # obj_spec_d is a dict
    obj_spec_d = type_spec_d[obj_name]
    if "subtype" not in obj_spec_d:
        raise Exception("subtype must be included in type's info")

    obj_subtype = obj_spec_d["subtype"]

    atomic_types = ["float", "string", "int", "bool", "pass"]
    if obj_subtype in atomic_types:
        validate_atomic_type(obj_spec_d["subtype"], obj, obj_name, obj_spec_d)
    else:
        if obj_subtype == "dict":
            if not isinstance(obj, dict):
                raise Exception(f"Object {obj_name} thought to be dict " + \
                                "is not, instead is " + str(type(obj)))
            # A few options: (dict_keys) or (dict_spec) or (unknown)
            if "dict_keys" in obj_spec_d:
                dict_keys_d = obj_spec_d["dict_keys"]
                for key_name, new_obj_name in dict_keys_d.items():
                    if key_name not in obj:
                        raise Exception(f"Object {obj_name} missing key: {key_name}")
                    check_object_against_types(new_obj_name,
                                               obj[key_name],
                                               type_spec_d)
                # There could also be optional keys if it's dict_keys
                if "optional_keys" in obj_spec_d:
                    optional_keys_d = obj_spec_d["optional_keys"]
                    for key_name, new_obj_name in optional_keys_d.items():
                        if key_name in obj:
                            check_object_against_types(new_obj_name,
                                                       obj[key_name],
                                                       type_spec_d)

            elif "dict_spec" in obj_spec_d:
                # Check for each key of obj
                # Single key mapped to single value
                spec_d = obj_spec_d["dict_spec"]
                if len(spec_d.keys()) != 1:
                    raise Exception("dict_spec needs to have one key and one value.")
                key_obj_name = list(spec_d.keys())[0]
                value_obj_name = spec_d[key_obj_name]
                for k in obj.keys():
                    check_object_against_types(key_obj_name,
                                               k,
                                               type_spec_d)
                    check_object_against_types(value_obj_name,
                                               obj[k],
                                               type_spec_d)
            elif "unknown" in obj_spec_d:
                pass
            else:
                raise Exception("dict object definitions must have either " + \
                                "dict_keys or dict_spec defined.")
        elif "list<" in obj_subtype:
            if not isinstance(obj, list):
                raise Exception(f"Object {obj_name} thought to be list " + \
                                "is not, instead is " + str(type(obj)))
            if list(obj_subtype)[-1] != ">":
                raise Exception("In list type definition, '>' must be last " + \
                                "part, instead " + list(obj_subtype)[-1])
            list_subtype = (obj_subtype.split("<")[1]).split(">")[0]
            if list_subtype == obj_name:
                raise Exception(f"Recursion error: {obj_name} has subtype {obj_subtype}.")
            for sublist_obj in obj:
                check_object_against_types(list_subtype, sublist_obj, type_spec_d)
        else:
            if obj_subtype not in type_spec_d:
                raise Exception(f"Object subtype {obj_subtype} not in type_spec_d")
            else:
                if obj_subtype == obj_name:
                    raise Exception(f"Recursion error: {obj_name} has subtype {obj_subtype}.")
                check_object_against_types(obj_subtype, obj, type_spec_d)




def validate_atomic_type(subtype_str, obj, obj_name, obj_spec_d):
    """
    *DOCDONE
    Args:
        subtype_str (var): Another name for variable
            ( var (string): Name of a variable )
        obj (pass): Unknown Object.
        obj_name (var): Name of a variable
            ( var (string): Name of a variable )
        obj_spec_d (spec_d): Spec d for an object
            ( spec_d (dict): The dict that holds the information about a single variable. )
            -keys:
                'subtype' -> subtype (string), String describing what the type of a variable is.
                'desc' -> desc (string), String describing a variable's meaning.
            -optional keys:
                '[dict_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[optional_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[dict_spec]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[restrictions]' -> restrictions_d (dict), The dict that holds restrictions for various objects.
                -optional keys:
                    '[regex]' -> string (string), standard python string
                    '[less_than]' -> float (float), standard python float
                    '[greater_than]' -> float (float), standard python float
                    '[decimal_max]' -> int (int), standard python int
    """
    if subtype_str == "string":
        if not isinstance(obj, str):
            raise Exception(f"String object not string: {obj_name}, instead: " + str(type(obj)))
        if "restrictions" in obj_spec_d:
            check_string_restrictions(obj, obj_spec_d["restrictions"], obj_name)
    elif subtype_str == "float":
        if not isinstance(obj, float):
            raise Exception(f"Float object not float: {obj_name}, instead: " + str(type(obj)))
        if "restrictions" in obj_spec_d:
            check_float_restrictions(obj, obj_spec_d["restrictions"], obj_name)
    elif subtype_str == "int":
        if not isinstance(obj, int):
            raise Exception(f"Int object not int: {obj_name}, instead: " + str(type(obj)))
        if "restrictions" in obj_spec_d:
            check_int_restrictions(obj, obj_spec_d["restrictions"], obj_name)
    elif subtype_str == "bool":
        if not isinstance(obj, bool):
            raise Exception(f"Int object not int: {obj_name}, instead: " + str(type(obj)))
    elif subtype_str == "pass":
        # We don't look into this one.
        pass
    else:
        raise Exception("Expecting subtype string to be one of 'float', 'string', 'int', " + \
                        f" 'bool'; instead {subtype_str}")


def check_string_restrictions(obj, restrictions_d, obj_name):
    """
    *DOCDONE
    Args:
        obj (pass): Unknown Object.
        restrictions_d (dict): The dict that holds restrictions for various objects.
        -optional keys:
            '[regex]' -> string (string), standard python string
            '[less_than]' -> float (float), standard python float
            '[greater_than]' -> float (float), standard python float
            '[decimal_max]' -> int (int), standard python int
        obj_name (var): Name of a variable
            ( var (string): Name of a variable )
    """
    possible_restrictions = ["regex", "is_file", "is_dir", "op_file", "one_of"]
    for x in restrictions_d.keys():
        if x not in possible_restrictions:
            raise Exception(f"key {x} not recognized as restriction for strings.")
    if "regex" in restrictions_d:
        regex_str = restrictions_d["regex"]
        logging.debug("Checking regex, regex str: " + regex_str)
        m = re.search(regex_str, obj)
        if not m:
            raise Exception("Could not find regex match for string: " + obj)
    if "is_file" in restrictions_d:
        if not os.path.isfile(obj):
            raise Exception("Expecting existing file at loc " + obj)
    if "is_dir" in restrictions_d:
        if not os.path.isdir(obj):
            raise Exception("Expecting existing dir at loc " + obj)
    if "op_file" in restrictions_d:
        if not os.path.isdir(os.path.dirname(obj)):
            raise Exception("Expecting existing dir at loc " + os.path.dirname(obj))
    if "one_of" in restrictions_d:
        one_of_list = restrictions_d["one_of"]
        if not isinstance(one_of_list, list):
            raise Exception("If defining a restricted vocabulary using " + \
                            "'one_of', the value for 'one_of' must be a list.")
        if obj not in one_of_list:
            raise Exception(f"Obj {obj} not in one_of_list: '" + \
                            "', '".join(one_of_list) + "'.")


def check_float_restrictions(obj, restrictions_d, obj_name):
    """
    *DOCDONE
    Args:
        obj (pass): Unknown Object.
        restrictions_d (dict): The dict that holds restrictions for various objects.
        -optional keys:
            '[regex]' -> string (string), standard python string
            '[less_than]' -> float (float), standard python float
            '[greater_than]' -> float (float), standard python float
            '[decimal_max]' -> int (int), standard python int
        obj_name (var): Name of a variable
            ( var (string): Name of a variable )
    """
    possible_restrictions = ["decimal_max", "less_than", "greater_than"]
    for x in restrictions_d.keys():
        if x not in possible_restrictions:
            raise Exception(f"key {x} not recognized as restriction for floats.")
    if "decimal_max" in restrictions_d:
        max_num_decimals = restrictions_d["decimal_max"]
        actual_num_decimals = len(str(obj).split(".")[1])
        if actual_num_decimals > max_num_decimals:
            raise Exception(f"Too many decimal points for object {obj}," + \
                            f" max number is {max_num_decimals}.")
    if "less_than" in restrictions_d:
        max_val = restrictions_d["less_than"]
        if obj > max_val:
            raise Exception(f"{obj} is greater than max value {max_val}.")
    if "greater_than" in restrictions_d:
        min_val = restrictions_d["greater_than"]
        if obj < min_val:
            raise Exception(f"{obj} is less than min value {min_val}.")


def check_int_restrictions(obj, restrictions_d, obj_name):
    """
    *DOCDONE
    Args:
        obj (pass): Unknown Object.
        restrictions_d (dict): The dict that holds restrictions for various objects.
        -optional keys:
            '[regex]' -> string (string), standard python string
            '[less_than]' -> float (float), standard python float
            '[greater_than]' -> float (float), standard python float
            '[decimal_max]' -> int (int), standard python int
        obj_name (var): Name of a variable
            ( var (string): Name of a variable )
    """
    possible_restrictions = ["less_than", "greater_than"]
    for x in restrictions_d.keys():
        if x not in possible_restrictions:
            raise Exception(f"key {x} not recognized as restriction for ints.")
    if "less_than" in restrictions_d:
        max_val = restrictions_d["less_than"]
        if obj > max_val:
            raise Exception(f"{obj} is greater than max value {max_val}.")
    if "greater_than" in restrictions_d:
        min_val = restrictions_d["greater_than"]
        if obj > min_val:
            raise Exception(f"{obj} is greater than min value {min_val}.")

# rets type_spec_d
def import_all_types(types_cfg_json_fp):
    """
    *DOCDONE
    Args:
        types_cfg_json_fp (string): Path to all type spec file.
            Restriction: is_file=1
    Returns:
        type_spec_d (dict): The dict that holds the information about all the variables.
        -maps var -> spec_d
            var (string): Name of a variable
            spec_d (dict): The dict that holds the information about a single variable.
            -keys:
                'subtype' -> subtype (string), String describing what the type of a variable is.
                'desc' -> desc (string), String describing a variable's meaning.
            -optional keys:
                '[dict_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[optional_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[dict_spec]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[restrictions]' -> restrictions_d (dict), The dict that holds restrictions for various objects.
                -optional keys:
                    '[regex]' -> string (string), standard python string
                    '[less_than]' -> float (float), standard python float
                    '[greater_than]' -> float (float), standard python float
                    '[decimal_max]' -> int (int), standard python int
    """

    type_spec_d = load_cfg_d(types_cfg_json_fp)
    types_list = type_spec_d["types"]
    type_spec_d = {
            "dict": {"subtype": "dict", "desc": "standard python dict"},
            "float": {"subtype": "float", "desc": "standard python float"},
            "string": {"subtype": "string", "desc": "standard python string"},
            "bool": {"subtype": "bool", "desc": "standard python bool"},
            "int": {"subtype": "int", "desc": "standard python int"},
            "None": {"subtype": "None", "desc": "None type"},
            "pass": {"subtype": "None", "desc": "Ignoring description."}
        }
    for type_info_d in types_list:
        type_name = type_info_d["name"]
        subtype_name = type_info_d["subtype"]
        if "list<" in subtype_name:
            subtype_name = (subtype_name.split("<")[1]).split(">")[0]
        if subtype_name not in type_spec_d:
            raise Exception(f"For type {type_name}, subtype " + \
                            f"{subtype_name} not found." )
        type_spec_d[type_name] = copy.deepcopy(type_info_d)
        del type_spec_d[type_name]["name"]

    logging.debug("Finished importing type spec d")
    return type_spec_d


# rets type_spec_d 
def load_cfg_d(types_cfg_json_fp):
    """
    *DOCDONE
    Args:
        types_cfg_json_fp (string): Path to all type spec file.
            Restriction: is_file=1
    Returns:
        type_spec_d (dict): The dict that holds the information about all the variables.
        -maps var -> spec_d
            var (string): Name of a variable
            spec_d (dict): The dict that holds the information about a single variable.
            -keys:
                'subtype' -> subtype (string), String describing what the type of a variable is.
                'desc' -> desc (string), String describing a variable's meaning.
            -optional keys:
                '[dict_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[optional_keys]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[dict_spec]' -> dict_keys_d (dict), The definition for the dict that holds dict keys
                -maps dict_key -> string
                    dict_key (string): A key for a dict to add to doc str
                    string (string): standard python string
                '[restrictions]' -> restrictions_d (dict), The dict that holds restrictions for various objects.
                -optional keys:
                    '[regex]' -> string (string), standard python string
                    '[less_than]' -> float (float), standard python float
                    '[greater_than]' -> float (float), standard python float
                    '[decimal_max]' -> int (int), standard python int
    """

    type_spec_d = json.loads(open(types_cfg_json_fp).read())
    if "types" not in type_spec_d:
        raise Exception("Types specification config dict must contain key 'types'")

    return type_spec_d


def test_2(types_cfg_json_fp, input_cfg_json_fp):
    """
    *DOCDONE
    Args:
        types_cfg_json_fp (string): Path to all type spec file.
            Restriction: is_file=1
        input_cfg_json_fp (string): Path to input config dict
            Restriction: is_file=1
    """
    logging.basicConfig(level=logging.DEBUG)
    type_spec_d = import_all_types(types_cfg_json_fp)
    cfg_d = json.loads(open(input_cfg_json_fp).read())
    check_cfg_d(cfg_d, type_spec_d)

def test_1(types_cfg_json_fp):
    """
    *DOCDONE
    Args:
        types_cfg_json_fp (string): Path to all type spec file.
            Restriction: is_file=1
    """
    type_spec_d = import_all_types(types_cfg_json_fp)
    print(type_spec_d)


def main():
    args = sys.argv
    help_str = "python3 validate_types.py types_cfg_json_fp, inp_cfg_d_json_fp 1"

    if args[-1] not in ["1"]:
        print("Not running.")
        print(help_str)
        sys.exit(1)
    elif args[-1] == "1":
        types_cfg_json_fp = args[1]
        input_cfg_json_fp = args[2]
        test_2(types_cfg_json_fp, input_cfg_json_fp)
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
