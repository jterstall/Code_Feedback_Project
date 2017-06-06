import os
import sys
import inspect
import redbaron
import itertools
import generate_feedback

ICP_module = {}
ICP_class = {}
line_numbers = {}
firstRun = True


def ICP_decorator(fn):
    def wrapper(*args, **kwargs):
        global ICP_module
        global ICP_class
        global line_numbers
        global firstRun

        if firstRun:
            ICP_class = fill_class_dict(ICP_class, os.getcwd())
            firstRun = False

        module_caller, module_callee, class_caller, class_callee, number_of_parameters, line_number_key, duplicate_call = retrieve_call_information(
            fn, args)
        if not duplicate_call:
            # Set requirement flags for adding an external module call
            different_module = module_caller != module_callee
            none_modules_present = None in (module_caller, module_callee)
            if different_module and not none_modules_present:
                line_numbers[line_number_key] = True
                ICP_module = add_external_call(
                    module_caller, module_callee, ICP_module, number_of_parameters)

            # Set requirement flags for adding an external class call
            different_class = class_caller != class_callee
            none_class_present = None in (class_caller, class_callee)
            if different_class and not none_class_present:
                line_numbers[line_number_key] = True
                ICP_class = add_external_call(
                    class_caller, class_callee, ICP_class, number_of_parameters)
        return fn(*args, **kwargs)
    return wrapper

# Skip specifies levels of stack to skip while getting caller name, skip=2
# is direct caller
def retrieve_call_information(fn, args):
    (caller_frame, caller_file_name, caller_line_number, _,
     _, _) = inspect.getouterframes(inspect.currentframe())[2]

    module_caller = caller_file_name.split('/')[-1].split('.py')[0]
    caller_line_number = str(caller_line_number)

    line_number_key = module_caller + '.' + caller_line_number
    if line_numbers.has_key(line_number_key):
        duplicate_line = True
        return None, None, None, None, None, None, duplicate_line
    else:
        duplicate_line = False

        # Retrieve module information
        module_callee = sys.modules[fn.__module__].__file__.split('/')[-1].split('.py')[0]

        # Retrieve class information
        class_caller = None
        if 'self' in caller_frame.f_locals:
            class_caller = module_caller.split('.py')[0] + "." + caller_frame.f_locals['self'].__class__.__name__

        class_callee = None
        if args and hasattr(args[0], '__class__'):
            class_callee = module_callee.split('.py')[0] + "." + args[0].__class__.__name__

        number_of_parameters = len(inspect.getargspec(fn)[0])

        return module_caller, module_callee, class_caller, class_callee, number_of_parameters, line_number_key, duplicate_line


# This function adds to the information-flow-based coupling value if an
# external call is detected
def add_external_call(caller_name, callee_name, ICP_dict, number_of_parameters):
    dict_key = caller_name + ":" + callee_name
    dict_key_2 = callee_name + ":" + caller_name
    if number_of_parameters == 0:
        number_of_parameters = 1

    # Add to ICP dictionary the external call weighted by the number of
    # parameters as described in bavota2013
    if dict_key not in ICP_dict and dict_key_2 not in ICP_dict:
        ICP_dict[dict_key] = number_of_parameters
    elif dict_key in ICP_dict:
        ICP_dict[dict_key] += number_of_parameters
    elif dict_key_2 in ICP_dict:
        ICP_dict[dict_key_2] += number_of_parameters

    return ICP_dict


def retrieve_files_in_dir(path):
    # Retrieve absolute path of all files
    files_in_dir = [os.path.join(dirpath, f) for (dirpath, _, filenames) in os.walk(
        path) for f in filenames if f.endswith(".py")]
    return files_in_dir


def fill_class_dict(class_dict, path):
    files_in_path = retrieve_files_in_dir(path)
    print os.getcwd()
    for file_name in files_in_path:
        classes = []
        with open(file_name) as f:
            red = redbaron.RedBaron(f.read())
        module = file_name.split('/')[-1].replace('.py', '.')
        for cls in red.find_all("ClassNode"):
            classes.append(module + cls.name)
        for combination in itertools.combinations(classes, 2):
            class_dict[combination[0]+":"+combination[1]] = 0
    return class_dict


def pass_result():
    generate_feedback.ICP_module_feedback(ICP_module)
    generate_feedback.ICP_class_feedback(ICP_class)
