from __future__ import division
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import generate_feedback
import numpy as np
import itertools
import redbaron
import argparse
import sys
import ICP
import ast
import os


def retrieve_source_code_files(files_in_dir, modules_in_dir):
    modules_source_code = {}
    for i, file_path in enumerate(files_in_dir):
        with open(file_path) as f:
            red = redbaron.RedBaron(f.read())
        for fn in red.find_all("DefNode"):
            key = modules_in_dir[i] + "." + fn.name
            source_code = ""
            for name in fn.find_all("NameNode"):
                source_code = source_code + " " + name.value
            modules_source_code[key] = source_code
    return modules_source_code


def retrieve_source_code_classes(files_in_dir, modules_in_dir):
    classes_source_code = {}
    classes_in_dir = []
    for i, file_path in enumerate(files_in_dir):
        with open(file_path) as f:
            red = redbaron.RedBaron(f.read())
        for cls in red.find_all("ClassNode"):
            classes_in_dir.append(modules_in_dir[i] + "." + cls.name)
            for fn in cls.find_all("DefNode"):
                key = modules_in_dir[i] + "." + cls.name + "." + fn.name
                source_code = ""
                for name in fn.find_all("NameNode"):
                    if not name.value == "ICP_decorator":
                        source_code = source_code + " " + name.value
                classes_source_code[key] = source_code
    return classes_in_dir, classes_source_code


# Compute Conceptual Coupling between Methods as described in bavota2013
def ccm(vector1, vector2):
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


# Compute Conceptual Coupling Between Modules (files or classes) as
# described in bavota2013
def ccbm(module1, module2, lsi_vectors):
    module1_vectors = [lsi_vectors[key]
                       for key in lsi_vectors.keys() if '.'.join(key.split('.')[:-1]) == module1]
    module2_vectors = [lsi_vectors[key]
                       for key in lsi_vectors.keys() if '.'.join(key.split('.')[:-1]) == module2]

    if module1_vectors == [] or module2_vectors == []:
        return 0

    ccm_sum = 0
    for module1_vector in module1_vectors:
        for module2_vector in module2_vectors:
            ccm_sum += ccm(module1_vector, module2_vector)

    # Return average ccm between two modules
    return ccm_sum / (len(module1_vectors) * len(module2_vectors))


# Compute ccbm scores between all possible combinations of modules
def compute_ccbm_scores(module_names_in_dir, lsi_vectors):
    ccbm_scores = {}
    for combination in itertools.combinations(module_names_in_dir, 2):
        ccbm_scores[combination] = ccbm(combination[0], combination[1], lsi_vectors)
    return sorted(ccbm_scores.items(), key=lambda x: x[1], reverse=True)


def retrieve_lsi_vectors(modules_source_code, dimension):
    source_code = list(modules_source_code.values())
    callables = list(modules_source_code.keys())

    # Compute tf-idf matrix
    vectorizer = TfidfVectorizer(sublinear_tf=True, use_idf=True,
                                 stop_words=None, smooth_idf=True)
    tf_idf = vectorizer.fit_transform(source_code)
    tf_idf_matrix = tf_idf.todense()

    # Dimension to reduce to with Latent Semantic Indexing
    amount_of_features = len(vectorizer.get_feature_names())
    print vectorizer.get_feature_names()
    if amount_of_features <= dimension:
        dimension = amount_of_features - 1

    # Reduce dimensionality of tf_idf matrix with SVD
    svd = TruncatedSVD(n_components=dimension)
    svdMatrix = svd.fit_transform(tf_idf_matrix)

    # Create dict where each callable corresponds with its LSI feature vector
    lsi_vectors = dict(zip(callables, svdMatrix))

    return lsi_vectors


def run_conceptual_coupling(path, dimension=100):
    files_in_dir = ICP.retrieve_files_in_dir(path)

    module_names_in_dir = [file_name.split('/')[-1].split('.py')[0] for file_name in files_in_dir]

    # Compute Conceptual Coupling between Files

    modules_source_code = retrieve_source_code_files(files_in_dir, module_names_in_dir)

    if modules_source_code:

        lsi_vectors = retrieve_lsi_vectors(modules_source_code, dimension)

        ccbf_scores = compute_ccbm_scores(module_names_in_dir, lsi_vectors)

        generate_feedback.CCBM_feedback(ccbf_scores,path)

    # Compute conceptual coupling between classes

    classes_in_dir, classes_source_code = retrieve_source_code_classes(
        files_in_dir, module_names_in_dir)

    if classes_source_code:

        lsi_vectors = retrieve_lsi_vectors(classes_source_code, dimension)

        ccbc_scores = compute_ccbm_scores(classes_in_dir, lsi_vectors)

        generate_feedback.CCBM_feedback(ccbc_scores,path)
