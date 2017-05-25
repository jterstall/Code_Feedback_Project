import os
import sys
import inspect
import generate_feedback

ICP_module = {}
ICP_class = {}

def ICP_decorator(fn):
    def wrapper(*args, **kwargs):
        global ICP_module
        global ICP_class

        call_information = retrieve_call_information(fn)

        number_of_parameters = call_information['number_of_parameters']

        module_caller = call_information['module_caller']
        module_callee = call_information['module_callee']

        # Set requirement flags for adding an external module call
        different_module = module_caller.split('/')[-1] != module_callee.split('/')[-1]
        none_modules_present = None in (module_caller, module_callee)

        if different_module and not none_modules_present:
            ICP_module = add_external_call(
            module_caller, module_callee, ICP_module, number_of_parameters, module_flag=True)

        # class_caller = call_information['class_caller']
        # class_callee = call_information['class_callee']
        #
        # # Set requirement flags for adding an external class call
        # different_class = class_caller != class_callee
        # none_class_present = None in (class_caller, class_callee)
        #
        # if different_class and not none_class_present:
        #     ICP_class = add_external_call(
        #         class_caller, class_callee, ICP_class, number_of_parameters, module_flag=False)
        return fn(*args, **kwargs)
    return wrapper


# Skip specifies levels of stack to skip while getting caller name, skip=2
# is direct caller
def retrieve_call_information(fn, skip=2):
    call_information = dict.fromkeys(['module_caller', 'module_callee', 'class_caller', 'class_callee'])

    # Retrieve frame from stack where caller is situated
    callerframe = sys._getframe(2)


    # Retrieve module information if present in users directory
    module_caller = inspect.getmodule(callerframe)
    call_information['module_caller'] = retrieve_module_file(module_caller)

    # call_information['module_caller'] = callerframe.f_code.co_filename


    module_callee = sys.modules[fn.__module__]
    call_information['module_callee'] = retrieve_module_file(module_callee)

    # Retrieve class information
    if 'self' in callerframe.f_locals:
        call_information['class_caller'] = callerframe.f_locals['self'].__class__

    if inspect.ismethod(fn):
        call_information['class_callee'] = fn.im_class

    call_information['number_of_parameters'] = len(inspect.getargspec(fn)[0])

    del callerframe

    return call_information

def retrieve_module_file(module):
    if module and hasattr(module, "__file__"):
        return module.__file__
    return None


# This function adds to the information-flow-based coupling value if an
# external call is detected
def add_external_call(caller_name, callee_name, ICP_dict, number_of_parameters, module_flag):
    if module_flag:
        caller_name = caller_name.split('/')[-1]
        callee_name = callee_name.split('/')[-1]
    dict_key = caller_name +"--->"+ callee_name
    if dict_key not in ICP_dict:
        ICP_dict[dict_key] = 0

    if number_of_parameters == 0:
        number_of_parameters = 1

    # Add to ICP dictionary the external call weighted by the number of
    # parameters as described in bavota2013
    ICP_dict[dict_key] += (1 * number_of_parameters)

    return ICP_dict

def pass_result():
    generate_feedback.ICP_module_feedback(ICP_module)
    generate_feedback.ICP_class_feedback(ICP_class)
