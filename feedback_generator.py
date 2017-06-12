from __future__ import division
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import os

def generate_feedback(CC_files, CC_classes, ICP_module, ICP_class, path):
    output_file = path + "Coupling_Feedback_Tool/COUPLING_FEEDBACK_TOOL_RESULTS.txt"
    with open(output_file, 'w+') as f:
        f.write(str(sorted(ICP_module.iteritems(), key=lambda x: x[1], reverse=True)))
        f.write("\n\n")
        f.write(str(sorted(ICP_class.iteritems(), key=lambda x: x[1], reverse=True)))
        f.write("\n\n")
        f.write(str(sorted(CC_files.iteritems(), reverse=True, key=lambda x: x[1])))
        f.write("\n\n")
        f.write(str(sorted(CC_classes.iteritems(), reverse=True, key = lambda x: x[1])))
    ICP_graph(ICP_module)
    ICP_graph(ICP_class)
    print ""
    print sorted(ICP_module.iteritems(), key=lambda x: x[1], reverse=True)
    print ""
    print sorted(ICP_class.iteritems(), key=lambda x: x[1], reverse=True)
    print ""
    print sorted(CC_files.iteritems(), reverse=True, key=lambda x: x[1])
    print ""
    print sorted(CC_classes.iteritems(), reverse=True, key = lambda x: x[1])
    print ""

    high_cc_files = [(key, value) for (key, value) in CC_files.iteritems() if value > 0.5]
    danger_zone_cc_files = dict((key, value) for (key, value) in CC_files.iteritems() if value >= 0.20 and value <= 0.5)

    high_cc_classes_same_file = [(key, value) for (key, value) in CC_classes.iteritems() if value > 0.5 and in_same_file(key[0], key[1])]
    high_cc_classes_different_file = [(key, value) for (key, value) in CC_classes.iteritems() if value > 0.5 and not in_same_file(key[0], key[1])]
    danger_zone_cc_classes_different_file = dict((key, value) for (key, value) in CC_classes.iteritems() if value >= 0.20 and value <= 0.5 and not in_same_file(key[0], key[1]))
    low_cc_classes_same_file = dict((key, value) for (key, value) in CC_classes.iteritems() if value <= 0.12 and in_same_file(key[0], key[1]))

    high_icp_files = [(key, value) for (key, value) in ICP_module.iteritems() if value >= 100]
    danger_zone_icp_files = dict((key, value) for (key, value) in ICP_module.iteritems() if value >= 15 and value < 100)

    high_icp_classes_same_file = [(key, value) for (key, value) in ICP_class.iteritems() if value >= 100 and in_same_file(key.split(':')[0], key.split(':')[1])]
    high_icp_classes_different_file = [(key, value) for (key, value) in ICP_class.iteritems() if value >= 100  and not in_same_file(key.split(':')[0], key.split(':')[1])]
    danger_zone_icp_classes_different_file = dict((key, value) for (key, value) in ICP_class.iteritems() if value >= 15 and value < 100 and not in_same_file(key.split(':')[0], key.split(':')[1]))
    low_icp_classes_same_file = [(key, value) for (key, value) in ICP_class.iteritems() if value <= 10 and in_same_file(key.split(':')[0], key.split(':')[1])]

    cc_keys_feedback_given = feedback_high_icp_class(high_icp_classes_different_file, CC_classes)
    feedback_high_cc_different_file_classes(high_cc_classes_different_file, cc_keys_feedback_given)
    feedback_danger_zone_files(danger_zone_icp_files, danger_zone_cc_files)
    feedback_danger_zone_classes(danger_zone_icp_classes_different_file, danger_zone_cc_classes_different_file)
    feedback_high_cc_same_file_classes(high_cc_classes_same_file)
    feedback_high_cc_files(high_cc_files)
    feedback_low_coupling(low_icp_classes_same_file, low_cc_classes_same_file, ICP_class, CC_classes)


    # Feedback cases:
    # TODO Possible permutations low coupling new structure of classes?


def feedback_high_cc_files(high_cc_files):
    given_merge_feedback = False
    given_possible_merge_feedback = False
    print_statement_high_cc = ""
    print_statement_low_cc = ""
    # (DONE) Hoge CC Files = duplicate code hoogstwaarshijnlijk, samenvoegen of een deel van de code splitsen
    if high_cc_files:
        for cc_cls in high_cc_files:
            if cc_cls[1] > 0.75:
                if given_merge_feedback:
                    print_statement_high_cc = print_statement_high_cc + '''
    {0}.py and {1}.py
                    '''.format(cc_cls[0][0], cc_cls[0][1])
                else:
                    given_merge_feedback = True
                    print_statement_high_cc = print_statement_high_cc + '''
    The following combination(s) of files seem to contain a lot of duplicate
    code between them. It would improve the maintainability of your
    code to create a new file that contains the duplicate code and executes that task.
    This ensures that this particular piece of code will be reusable and modifiable
    for multiple files. An alternative solution could be to merge these two files into one:

    {0}.py and {1}.py
                    '''.format(cc_cls[0][0], cc_cls[0][1])
            else:
                if given_possible_merge_feedback:
                    print_statement_low_cc = print_statement_low_cc + '''
    {0}.py and {1}.py
                    '''.format(cc_cls[0][0], cc_cls[0][1])
                else:
                    given_possible_merge_feedback = True
                    print_statement_low_cc = print_statement_low_cc + '''
    The following combination(s) of files seem to contain parts of code between them
    that perform similar tasks. It would improve the maintainablity of your code to identify
    these tasks and create a new file/class that will exclusively execute this task which
    will be reusable by multiple files:

    {0}.py and {1}.py
                    '''.format(cc_cls[0][0], cc_cls[0][1])

    print(print_statement_high_cc)
    print(print_statement_low_cc)


def feedback_high_cc_same_file_classes(high_cc_classes_same_file):
    given_feedback = False
    # (DONE) Hoge CC Class en zelfde file >0.5 = duplicate code, samenvoegen van classes?
    if high_cc_classes_same_file:
        for cc_cls in high_cc_classes_same_file:
            if cc_cls[1] >= 0.75:
                if given_feedback:
                    print '''
    {0} and {1}
                    '''.format(cc_cls[0][0], cc_cls[0][1])
                else:
                    given_feedback = True
                    print '''
    The following combination(s) of classes that are located in the same file seem to contain
    a lot of duplicate code or perform (nearly) the exact same task. It would be better
    to merge these two classes into one class to improve the modularization of your code.
    Ensuring that each class has only one well-defined task that it performs will make sure
    that your code will be easily understood by others:

    {0} and {1}
                    '''.format(cc_cls[0][0], cc_cls[0][1])

def feedback_danger_zone_classes(danger_zone_icp_classes_different_file, danger_zone_cc_classes_different_file):
    given_feedback = False
    # (Done) Danger zone CC Class, Danger zone ICP Class different file = samenvoegen
    for icp_cls in danger_zone_icp_classes_different_file.iteritems():
        new_key1, new_key2 = generate_key_combinations(icp_cls[0])
        if new_key1 in danger_zone_cc_classes_different_file or new_key2 in danger_zone_cc_classes_different_file:
            if given_feedback:
                print '''
    {0} and {1}
                '''.format(icp_cls[0].split(':')[0], icp_cls[0].split(':')[1])
            else:
                given_feedback = True
                print '''
    The following combination(s) of classes seem to be performing similar tasks and are
    very dependent on each other. Because they are located in different files, it means that
    changes to one class can not be made without it having an effect on a different file.
    If structurally possible, it would be best to move these classes into the same file to
    ensure that dependencies between files is limited and that each file contains classes
    that perform tasks which are similar. This ensures that your program will be easily
    modifiable and maintainable:

    {0} and {1}
                '''.format(icp_cls[0].split(':')[0], icp_cls[0].split(':')[1])


def feedback_danger_zone_files(danger_zone_icp_files, danger_zone_cc_files):
    given_feedback = False
    # (Done) Danger zone CC Files Danger zone ICP files different file = erg gecoupled
    for icp_file in danger_zone_icp_files.iteritems():
        new_key1, new_key2 = generate_key_combinations(icp_file[0])
        if new_key1 in danger_zone_cc_files or new_key2 in danger_zone_cc_files:
            if given_feedback:
                print '''
    {0}.py and {1}.py
                '''.format(icp_file[0].split(':')[0], icp_file[0].split(':')[1])
            else:
                given_feedback = True
                print '''
    The following combination(s) of files seem to perform similar tasks and are very
    dependent on each other. If possible, it would be best to merge these files into one file
    or to rewrite them in such a way that each file performs similar tasks and are not dependent
    on other files. This ensures that your code can easily be modified without affecting other
    files and it will ensure that the structure of your program is easily understood by others:

    {0}.py and {1}.py
                '''.format(icp_file[0].split(':')[0], icp_file[0].split(':')[1])


def feedback_high_icp_class(high_icp_classes_different_file, CC_classes):
    given_merge_feedback = False
    given_move_feedback = False
    # (DONE) Hoge ICP Class en andere file = samenvoegen als cc ook hoog / verplaatsen als niet
    print_statement_high_cc = ""
    print_statement_low_cc = ""
    cc_keys_feedback_given = []
    for icp_cls in high_icp_classes_different_file:
        new_key1, new_key2 = generate_key_combinations(icp_cls[0])
        if new_key1 in CC_classes:
            cc_score = CC_classes[new_key1]
            cc_keys_feedback_given.append(new_key1)
        elif new_key2 in CC_classes:
            cc_score = CC_classes[new_key2]
            cc_keys_feedback_given.append(new_key2)
        if cc_score > 0.75:
            if given_merge_feedback:
                print_statement_high_cc = print_statement_high_cc + '''
    {0} and {1}
                '''.format(icp_cls[0].split(':')[0], icp_cls[0].split(':')[1])
            else:
                given_merge_feedback = True
                print_statement_high_cc = print_statement_high_cc + '''
    The following combination(s) of classes seem to be too dependent on each other to function
    without the other. These classes also seem to perform (nearly) the same task or contain
    duplicate code between them. To improve the maintainability of your code, it would be
    better to move these classes into the same file so that dependencies are limited to one
    file. If possible, it would be best to merge these classes into a single class to make
    sure that each class performs its own well-defined task:

    {0} and {1}
                '''.format(icp_cls[0].split(':')[0], icp_cls[0].split(':')[1])
        else:
            if given_move_feedback:
                print_statement_low_cc = print_statement_low_cc + '''
    {0} and {1}
                '''.format(icp_cls[0][0], icp_cls[0][1])
            else:
                given_move_feedback = True
                print_statement_low_cc = print_statement_low_cc + '''
    The following combination(s) of classes are extremely dependent on each other.
    To improve the maintainability of your code, it would be best to move these classes
    into the same file so that dependencies are limited to classes in the same file:

    {0} and {1}
                '''.format(icp_cls[0].split(':')[0], icp_cls[0].split(':')[1])
    print(print_statement_high_cc)
    print(print_statement_low_cc)
    return cc_keys_feedback_given

def feedback_high_cc_different_file_classes(high_cc_classes_different_file, cc_keys_feedback_given):
    given_merge_feedback = False
    given_move_feedback = False
    print_statement_high_cc = ""
    print_statement_low_cc = ""
    # (Done) Hoge CC Class en andere file = verplaatsen in dezelfde file, misschien samenvoegen (ligt eraan hoe hoog)
    if high_cc_classes_different_file:
        for cc in high_cc_classes_different_file:
            if not cc[0] in cc_keys_feedback_given:
                if cc[1] >= 0.75:
                    if given_merge_feedback:
                        print_statement_high_cc = print_statement_high_cc + '''
    {0} and {1}
                        '''.format(cc[0][0], cc[0][1])
                    else:
                        given_merge_feedback = True
                        print_statement_high_cc = print_statement_high_cc + '''
    The following combination(s) of classes seem to perform the same task conceptually and
    are located in different files. This means that either these classes contain a lot of
    duplicate code between them or these classes perform almost the same task. To improve
    the maintainability of your code, it would be best to move these classes into the same
    file and if possible, to also merge them into a single class. This will ensure that classes
    with similar tasks are grouped together and that each class has its own well-defined task:

    {0} and {1}
                        '''.format(cc[0][0], cc[0][1])
                else:
                    if given_move_feedback:
                        print_statement_low_cc = print_statement_low_cc + '''
    {0} and {1}
                        '''.format(cc[0][0], cc[0][1])
                    else:
                        given_move_feedback = True
                        print_statement_low_cc = print_statement_low_cc + '''
    The following combination(s) of classes seem to perform similar tasks while they are
    located in separate files. It would be best to move these classes into one file to
    make sure that each class with a similar task is grouped in one file which will improve
    how easily your code is understood by others:

    {0} and {1}
                        '''.format(cc[0][0], cc[0][1])
    print(print_statement_high_cc)
    print(print_statement_low_cc)


def feedback_low_coupling(low_icp_classes_same_file, low_cc_classes_same_file, ICP_class, CC_classes):
    # (Done) Lage CC Class + Lage ICP Class en zelfde file splitten
    low_coupling_same_file = []
    for icp_cls in low_icp_classes_same_file:
        new_key1, new_key2 = generate_key_combinations(icp_cls[0])
        if new_key1 in low_cc_classes_same_file or new_key2 in low_cc_classes_same_file:
            low_coupling_same_file.append(new_key2)

    low_average_coupling_feedback_given = False
    # (Done) Veel classes in 1 file en gemiddelde ICP en CC = splitten
    classes_per_module = {}
    for (key, value) in ICP_class.iteritems():
        split_key = key.split(':')
        cls1 = split_key[0]
        cls2 = split_key[1]
        module1 = '.'.join(cls1.split('.')[:-1])
        module2 = '.'.join(cls2.split('.')[:-1])
        if module1 == module2:
            if module1 not in classes_per_module:
                classes_per_module[module1] = []
            classes = classes_per_module[module1]
            if cls1 not in classes:
                classes.append(cls1)
            if cls2 not in classes:
                classes.append(cls2)
    indices_feedback_given = []
    for key in classes_per_module.keys():
        classes = classes_per_module[key]
        if len(classes) >= 2:
            if low_average_coupling(classes, ICP_class, CC_classes):
                print_statement = ""
                for i, cls in enumerate(low_coupling_same_file):
                    if cls[0].split('.')[0] == key:
                        indices_feedback_given.append(i)
                        print_statement = print_statement + '''
    {0} and {1}
                        '''.format(cls[0], cls[1])
                if print_statement:
                    if low_average_coupling_feedback_given:
                        print '''
    The same as above applies to file {0}.py as well. Classes that can be split are:
                        '''.format(key)
                        print print_statement
                    else:
                        low_average_coupling_feedback_given = True
                        print '''
    Classes in {0}.py are not dependent on each other nor do they seem to perform similar
    tasks. If possible in the structure of your program, it would be better to split the
    classes in this file into separate files. Class combination(s) that can be split are
    the following classes (file_location.class_name):
                        '''.format(key)
                        print print_statement

    low_coupling_feedback = False
    for i, cls in enumerate(low_coupling_same_file):
        if i not in indices_feedback_given:
            if low_coupling_feedback:
                print '''
    {0} and {1}
                '''.format(cls[0], cls[1])
            else:
                low_coupling_feedback = True
                print '''
    The following class combinations(s) seem to perform dissimilar tasks and
    are not dependent on each other but are located in the same file. If possible it would be
    better to split these classes into separate files. Only do this if doesn't interfere
    with dependencies of other classes in the file. Aim to create files that contain classes
    that perform similar tasks and which are not too dependent on classes in other files:

    {0} and {1}
                '''.format(cls[0], cls[1])

def low_average_coupling(classes, ICP_class, CC_class):
    class_combinations = itertools.combinations(classes, 2)
    amount_of_combinations = 0
    ICP_sum = 0
    CC_sum = 0
    for combination in class_combinations:
        amount_of_combinations += 1
        key1_cc = (combination[0], combination[1])
        key2_cc = (combination[1], combination[0])
        key1_icp = combination[0] + ":" + combination[1]
        key2_icp = combination[1] + ":" + combination[0]
        if key1_icp in ICP_class:
            ICP_sum += ICP_class[key1_icp]
        elif key2_icp in ICP_class:
            ICP_sum += ICP_class[key2_icp]
        if key1_cc in CC_class:
            CC_sum += CC_class[key1_cc]
        if key2_cc in CC_class:
            CC_sum += CC_class[key2_cc]
    if (CC_sum / amount_of_combinations) <= 0.12 and (ICP_sum / amount_of_combinations) <= 5:
        return True
    return False

def generate_key_combinations(key):
    split_key = key.split(':')
    return (split_key[0], split_key[1]), (split_key[1], split_key[0])


def in_same_file(key1, key2):
    return key1.split('.')[:-1] == key2.split('.')[:-1]


def ICP_graph(ICP_dict):
    if len(ICP_dict) > 0:
        G = nx.DiGraph()
        for dependency, weight in ICP_dict.iteritems():
            dependency_components = dependency.split(':')
            G.add_edge(dependency_components[0], dependency_components[1], calls=weight)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True)
        calls = nx.get_edge_attributes(G, 'calls')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=calls)
        plt.show()
