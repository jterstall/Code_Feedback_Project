import ICP
import re
import baron.baron

def prepare_files(file_path):
    with open(file_path, 'r') as f:
        print f
        fst = baron.parse(f.read())
        source_code = baron.dumps(fst)
        # lines = f.readlines()
        # lines_to_delete = []
        # for i, line in enumerate(lines):
        #     if "print " in line:
        #         new_line = re.split('\w', line)[0].replace('\t', '    ') + 'pass \n'
        #         lines[i] = new_line
            # if "#" in line:
            #     lines_to_delete.append(i)
    # with open(file_path, 'w') as f:
        # for i, line in enumerate(lines):
        #     if i not in lines_to_delete:
        #         f.write(line)

def main():
    path = '/home/jterstall/Documents/Afstudeerproject_AI/Code/student_code/Redbaron_print_error'
    files_in_dir = ICP.retrieve_files_in_dir(path)
    for file_path in files_in_dir:
        prepare_files(file_path)

if __name__ == '__main__':
    main()
