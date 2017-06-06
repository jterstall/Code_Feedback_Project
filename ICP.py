import os
import sys
import json
import inspect
import redbaron
import subprocess


def suppress_output():
    sys.stdout = open(os.devnull, "w")


def allow_output():
    sys.stdout = sys.__stdout__


def retrieve_files_in_dir(path):
    # Retrieve absolute path of all files
    files_in_dir = [os.path.join(dir_path, f) for (dir_path, _, filenames) in os.walk(
    path) for f in filenames if f.endswith(".py") and not "Coupling_Feedback_Tool" in dir_path]
    return files_in_dir


def decorate_all_modules(file_list, main_file, path):
    for file_path in file_list:
        decorate_redbaron(file_path, main_file, path)


def decorate_redbaron(file_name, main_file, path):
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
            if len(from_import_statements) == 1:
                last_from_import_statement = from_import_statements[0]
            else:
                last_from_import_statement = from_import_statements[-1]
            indentation_level = len(str(last_from_import_statement.indentation))
            if indentation_level > 0:
                last_from_import_statement.decrease_indentation(indentation_level)
            last_from_import_statement.insert_after("import ICP_decorator")
            sys_path_insert_code = "sys.path.insert(0, r'%s')" % os.getcwd()
            last_from_import_statement.insert_after(sys_path_insert_code)
            last_from_import_statement.insert_after("import sys")
            if indentation_level > 0:
                last_from_import_statement.increase_indentation(indentation_level)

            red.find_all("DefNode").apply(lambda node: node.decorators.append("@ICP_decorator.ICP_decorator"))
        elif not from_import_statements and not decorator_import_present:
            # Insert necessary code
            red[0].insert_before("import ICP_decorator")
            sys_path_insert_code = "sys.path.insert(0, r'%s')" % os.getcwd()
            red[0].insert_before(sys_path_insert_code)
            red[0].insert_before("import sys")
            red.find_all("DefNode").apply(lambda node: node.decorators.append("@ICP_decorator.ICP_decorator"))

        # Main file needs to send resulting data to feedback generation script
        if file_name.split('/')[-1] == main_file:
            if not str(red[-1].name) == "ICP_decorator":
                red[-1].insert_after("ICP_decorator.store_result()")

        file_name = path + "Coupling_Feedback_Tool/" + file_name.split(path)[-1]
        with open(file_name, "w+") as f:
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
    # os.system(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

    # Revert working directory
    os.chdir(old_path)

def retrieve_ICP_results(path):
    ICP_class_result_path = path + '/ICP_class_result.json'
    ICP_module_result_path = path + '/ICP_module_result.json'

    with open(ICP_class_result_path, 'r') as f:
        try:
            ICP_class = json.load(f)
        except ValueError:
            ICP_class = {}
            print "Something went wrong..."
    with open(ICP_module_result_path, 'r') as f:
        try:
            ICP_module = json.load(f)
        except ValueError:
            ICP_module = {}
            print "Something went wrong..."
    return ICP_module, ICP_class



def run_ICP(main_file, path, optional_args):
    new_path = path + "Coupling_Feedback_Tool/"

    # If feedback folder exists, script was already run to decorate
    if not os.path.exists(new_path):
        os.makedirs(new_path)
        files_in_dir = retrieve_files_in_dir(path)
        decorate_all_modules(files_in_dir, main_file, path)

    run_file(main_file, new_path, optional_args)

    ICP_module, ICP_class = retrieve_ICP_results(new_path)
    return ICP_module, ICP_class
