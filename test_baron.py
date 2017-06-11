import os
import sys
import redbaron

def retrieve_files_in_dir(path):
    # Retrieve absolute path of all files
    files_in_dir = [os.path.join(dir_path, f) for (dir_path, _, filenames) in os.walk(
    path) for f in filenames if f.endswith(".py")]

    return files_in_dir

def main():
    path_to_file = sys.argv[1]
    files_in_dir = retrieve_files_in_dir(path_to_file)
    for f in files_in_dir:
        with open(f, 'r') as f:
            red = redbaron.RedBaron(f.read())



if __name__ == '__main__':
    main()
