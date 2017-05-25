import os
import sys
import inspect
import argparse
import redbaron
import subprocess
import generate_feedback


def suppress_output():
    sys.stdout = open(os.devnull, "w")


def allow_output():
    sys.stdout = sys.__stdout__


def retrieve_files_in_dir(path):
    # Retrieve absolute path of all files
    files_in_dir = [os.path.join(dirpath, f) for (dirpath, _, filenames) in os.walk(
    path) for f in filenames if f.endswith(".py")]
    return files_in_dir


def decorate_all_modules(file_list, main_file):
    for file_path in file_list:
        decorate_redbaron(file_path, main_file)


def decorate_redbaron(file_name, main_file):
    if not file_name.split('/')[-1] == "__init__.py":
        with open(file_name) as f:
            red = redbaron.RedBaron(f.read())

        # Detect if script was run before by detecting the ICP_decorator import
        decorator_import_present = False
        for import_statement in red.find_all("ImportNode"):
            import_name = import_statement.name
            if str(import_name) == "ICP_decorator":
                decorator_import_present = True
                break

        # Program has not been run before on this particular assignment
        # Prevent inserting before __future__ imports
        from_import_statements = red.find_all("FromImportNode")
        if from_import_statements and not decorator_import_present:
            last_from_import_statement = from_import_statements[-1]
            last_from_import_statement.insert_after("import ICP_decorator")
            sys_path_insert_code = "sys.path.insert(0, r'%s')" % os.getcwd()
            last_from_import_statement.insert_after(sys_path_insert_code)
            last_from_import_statement.insert_after("import sys")
            if file_name.split('/')[-1] == main_file:
                red[-1].insert_after("ICP_decorator.pass_result()")
            red.find_all("DefNode").apply(lambda node: node.decorators.append("@ICP_decorator.ICP_decorator"))
        elif not from_import_statements and not decorator_import_present:
            # Insert necessary code
            red[0].insert_before("import ICP_decorator")
            sys_path_insert_code = "sys.path.insert(0, r'%s')" % os.getcwd()
            red[0].insert_before(sys_path_insert_code)
            red[0].insert_before("import sys")
            # Main file needs to send resulting data to feedback generation script
            if file_name.split('/')[-1] == main_file:
                red[-1].insert_after("ICP_decorator.pass_result()")
            red.find_all("DefNode").apply(lambda node: node.decorators.append("@ICP_decorator.ICP_decorator"))

        with open(file_name, "w") as f:
            f.write(red.dumps())

def run_file(file_name, path, optional_args):
    # Change working directory
    old_path = os.getcwd()
    os.chdir(path)
    file_path = '"' + path+file_name+ '"'
    if optional_args:
        # Temporarily add file_path to optional_args for easy processing into command
        optional_args.insert(0, file_path)
        cmd = "python %s" % ' '.join(optional_args)
    else:
        cmd = "python %s" % file_path
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, error = proc.communicate()
    print output
    # Revert working directory
    os.chdir(old_path)


# Function handles input to this script
def init_arg_parser():
    parser = argparse.ArgumentParser(
        description="Feedback program based on coupling metrics")
    parser.add_argument(
        "path", help="Directory where student assignment is stored (absolute path)")
    parser.add_argument(
        "main_file", help="Main file of student assignment used to run the program", type=str)
    parser.add_argument(
        "--suppress", help="Suppresses student assignment output", action='store_true')
    parser.add_argument("optional_args", nargs="*",
                        help="Any arguments necessary for passing on to student program in command line")
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

    files_in_dir = retrieve_files_in_dir(path)

    decorate_all_modules(files_in_dir, main_file)

    run_file(main_file, path, optional_args)

    allow_output()

if __name__ == '__main__':
    main()
