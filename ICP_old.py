import os
import sys
import inspect
import argparse
import subprocess
import ICP_decorator


def suppress_output():
    sys.stdout = open(os.devnull, "w")


def allow_output():
    sys.stdout = sys.__stdout__


def decorate_all_modules(module_list, path):
    # Change working directory
    sys.path.append(path)
    old_path = os.getcwd()
    os.chdir(path)
    for module_name in module_list:
        module = __import__(module_name)
        decorate_functions_methods(module)
    # Revert working directory
    os.chdir(old_path)


def decorate_functions_methods(module):
    # Decorate all methods
    for _, cls in inspect.getmembers(module, inspect.isclass):
        for method_name, method in inspect.getmembers(cls, inspect.ismethod):
            setattr(cls, method_name,
                    ICP_decorator.ICP_decorator(method))

    # Decorate all functions
    for fn_name, fn in inspect.getmembers(module, inspect.isfunction):
        setattr(module, fn_name, ICP_decorator.ICP_decorator(fn))


def retrieve_modules_in_dir(path, modules_to_exclude):
    modules_in_dir = []
    # Retrieve relative file paths of all python files in path
    files_in_dir = [os.path.relpath(os.path.join(dirpath, f), path) for (
        dirpath, _, filenames) in os.walk(path) for f in filenames]
    for f in files_in_dir:
        # Check if python file and if module should be excluded
        if f.endswith(".py") and f.split("/")[-1] not in modules_to_exclude:
            # Place in list with correct form to be able to call module (path.module_name)
            f = f.replace("/", ".")
            modules_in_dir.append(f.split(".py")[0])
    return modules_in_dir


def run_file(filename, optional_args, path):
    # Change working directory
    old_path = os.getcwd()
    os.chdir(path)
    execfile(filename, globals())
    # Revert working directory
    os.chdir(old_path)


# Function handles input to this script
def init_arg_parser():
    parser = argparse.ArgumentParser(
        description="Feedback program based on coupling metrics")
    parser.add_argument(
        "main_file", help="Main file of student assignment used to run the program", type=str)
    parser.add_argument(
        "path", help="Directory where student assignment is stored")
    parser.add_argument(
        "--suppress", help="Suppresses student assignment output", action='store_true')
    parser.add_argument("optional_args", nargs="*",
                        help="Any arguments necessary for passing on to student program")
    # Retrieve user input
    args, unknown = parser.parse_known_args()
    args.optional_args.extend(unknown)
    return args


def main():
    args = init_arg_parser()

    if args.suppress:
        suppress_output()

    main_file = args.main_file

    path = args.path

    optional_args = args.optional_args

    # Change user input args in sys
    if optional_args:
        sys.argv = [main_file] + optional_args
    else:
        sys.argv = [main_file]

    modules_to_exclude = ["ICP_decorator.py", "ICP.py", "CCBC.py"]

    modules_in_dir = retrieve_modules_in_dir(path, modules_to_exclude)

    decorate_all_modules(modules_in_dir, path)

    run_file(main_file, optional_args, path)

    allow_output()

    # Retrieve Information-flow-based Coupling between modues
    ICP_module = ICP_decorator.ICP_module
    ICP_class = ICP_decorator.ICP_class

    # print max([ICP_module[x][y] for x in ICP_module for y in ICP_module[x]])

    print "ICP between modules: %s" % ICP_module
    print "ICP between classes: %s" % ICP_class


if __name__ == '__main__':
    main()
