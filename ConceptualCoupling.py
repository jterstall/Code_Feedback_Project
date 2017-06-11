from __future__ import division
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import numpy as np
import itertools
import redbaron
import math
import sys
import ICP
import os

def retrieve_files_in_dir(path):
    # Retrieve absolute path of all files
    return [os.path.join(dir_path, f) for (dir_path, _, filenames) in os.walk(path) for f in filenames if f.endswith(".py") and not "Coupling_Feedback_Tool" in dir_path]


def retrieve_source_code_files(files_in_dir, modules_in_dir):
    modules_source_code = {}
    vocabulary_modules = ""
    for i, file_path in enumerate(files_in_dir):
        with open(file_path) as f:
            red = redbaron.RedBaron(f.read())
        for fn in red.find_all("DefNode"):
            source_code = fn.dumps()
            key = modules_in_dir[i] + "." + fn.name
            for comment in fn.find_all("CommentNode"):
                vocabulary_modules = vocabulary_modules + " " + comment.value
            for name in fn.find_all("NameNode"):
                vocabulary_modules = vocabulary_modules + " " + name.value
            modules_source_code[key] = source_code

    return modules_source_code, vocabulary_modules


def retrieve_source_code_classes(files_in_dir, modules_in_dir):
    classes_source_code = {}
    classes_in_dir = []
    vocabulary_classes = ""
    for i, file_path in enumerate(files_in_dir):
        with open(file_path) as f:
            red = redbaron.RedBaron(f.read())
        for cls in red.find_all("ClassNode"):
            classes_in_dir.append(modules_in_dir[i] + "." + cls.name)
            for fn in cls.find_all("DefNode"):
                source_code = fn.dumps()
                for comment in fn.find_all("CommentNode"):
                    vocabulary_classes = vocabulary_classes + " " + comment.value
                key = modules_in_dir[i] + "." + cls.name + "." + fn.name
                for name in fn.find_all("NameNode"):
                    vocabulary_classes = vocabulary_classes + " " + name.value
                classes_source_code[key] = source_code

    return classes_in_dir, classes_source_code, vocabulary_classes


# Compute Conceptual Coupling between Methods as described in bavota2013
def ccm(vector1, vector2):
    ccm = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
    if math.isnan(ccm):
        ccm = 0
    return ccm

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
    return ccbm_scores


def retrieve_lsi_vectors(modules_source_code, dimension, vocabulary):
    source_code = list(modules_source_code.values())
    callables = list(modules_source_code.keys())

    # Compute tf-idf matrix
    vectorizer = TfidfVectorizer(sublinear_tf=True, use_idf=True,
                                 stop_words=['#', 'self', 'range', 'enumerate', 'len', 'open', 'xrange'],
                                 smooth_idf=True, vocabulary=vocabulary)
    tf_idf = vectorizer.fit_transform(source_code)
    tf_idf_matrix = tf_idf.todense()

    # Dimension to reduce to with Latent Semantic Indexing
    amount_of_features = len(vectorizer.get_feature_names())
    if amount_of_features <= dimension:
        dimension = amount_of_features - 1

    # Reduce dimensionality of tf_idf matrix with SVD
    svd = TruncatedSVD(n_components=dimension)
    svdMatrix = svd.fit_transform(tf_idf_matrix)

    # Create dict where each callable corresponds with its LSI feature vector
    lsi_vectors = dict(zip(callables, svdMatrix))

    return lsi_vectors


def run_conceptual_coupling(path, dimension=100):
    files_in_dir = retrieve_files_in_dir(path)

    module_names_in_dir = [file_name.split('/')[-1].split('.py')[0] for file_name in files_in_dir]

    # Compute Conceptual Coupling between Files

    modules_source_code, vocabulary_modules = retrieve_source_code_files(files_in_dir, module_names_in_dir)

    ccbf_scores = {}

    if modules_source_code:

        lsi_vectors = retrieve_lsi_vectors(modules_source_code, dimension, list(set(vocabulary_modules.split())))

        ccbf_scores = compute_ccbm_scores(module_names_in_dir, lsi_vectors)

    # Compute conceptual coupling between classes

    classes_in_dir, classes_source_code, vocabulary_classes = retrieve_source_code_classes(files_in_dir, module_names_in_dir)

    ccbc_scores = {}

    if classes_source_code:

        lsi_vectors = retrieve_lsi_vectors(classes_source_code, dimension, list(set(vocabulary_classes.split())))

        ccbc_scores = compute_ccbm_scores(classes_in_dir, lsi_vectors)

    return ccbf_scores, ccbc_scores
