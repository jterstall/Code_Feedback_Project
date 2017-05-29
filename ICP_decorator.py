import sys
import inspect
import generate_feedback

ICP_module = {}
ICP_class = {}
line_numbers = {}

def ICP_decorator(fn):
    def wrapper(*args, **kwargs):
        global ICP_module
        global ICP_class
        global line_numbers

        module_caller, module_callee, class_caller, class_callee, number_of_parameters, line_number_key, duplicate_call = retrieve_call_information(fn, args)
        if not duplicate_call:
            # Set requirement flags for adding an external module call
            different_module = module_caller != module_callee
            none_modules_present = None in (module_caller, module_callee)
            if different_module and not none_modules_present:
                line_numbers[line_number_key] = True
                ICP_module = add_external_call(module_caller, module_callee, ICP_module, number_of_parameters)

            # Set requirement flags for adding an external class call
            different_class = class_caller != class_callee
            none_class_present = None in (class_caller, class_callee)
            if different_class and not none_class_present:
                line_numbers[line_number_key] = True
                ICP_class = add_external_call(class_caller, class_callee, ICP_class, number_of_parameters)
        return fn(*args, **kwargs)
    return wrapper


# Skip specifies levels of stack to skip while getting caller name, skip=2
# is direct caller
def retrieve_call_information(fn, args):
    (caller_frame, caller_file_name, caller_line_number, _, _, _) = inspect.getouterframes(inspect.currentframe())[2]

    module_caller = caller_file_name.split('/')[-1]
    caller_line_number = str(caller_line_number)

    line_number_key = module_caller+'.'+caller_line_number
    if line_numbers.has_key(line_number_key):
        duplicate_line = True
        return None, None, None, None, None, None, duplicate_line
    else:
        duplicate_line = False

        # Retrieve module information
        module_callee = sys.modules[fn.__module__].__file__.split('/')[-1]

        # Retrieve class information
        class_caller = None
        if 'self' in caller_frame.f_locals:
            class_caller = str(caller_frame.f_locals['self'].__class__)

        class_callee = None
        if args and hasattr(args[0], '__class__'):
            class_callee = str(args[0].__class__)

        number_of_parameters = len(inspect.getargspec(fn)[0])

        return module_caller, module_callee, class_caller, class_callee, number_of_parameters, line_number_key, duplicate_line


# This function adds to the information-flow-based coupling value if an
# external call is detected
def add_external_call(caller_name, callee_name, ICP_dict, number_of_parameters):
    dict_key = caller_name +"--->"+ callee_name
    if number_of_parameters == 0:
        number_of_parameters = 1

    # Add to ICP dictionary the external call weighted by the number of
    # parameters as described in bavota2013
    if dict_key not in ICP_dict:
        ICP_dict[dict_key] = number_of_parameters
    else:
        ICP_dict[dict_key] += number_of_parameters


    return ICP_dict

def pass_result():
    generate_feedback.ICP_module_feedback(ICP_module)
    generate_feedback.ICP_class_feedback(ICP_class)
