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


def retrieve_source_code(files_in_dir, modules_in_dir):
    modules_source_code = {}
    for i in range(len(files_in_dir)):
        print files_in_dir[i]
        with open(files_in_dir[i]) as f:
            red = redbaron.RedBaron(f.read())
        for fn in red.find_all("DefNode"):
            key = modules_in_dir[i] + "." + fn.name
            modules_source_code[key] = fn.dumps()
    return modules_source_code


# Compute Conceptual Coupling between Methods as described in bavota2013
def ccm(vector1, vector2):
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


# Compute Conceptual Coupling Between Modules as described in bavota2013
def ccbm(module1, module2, lsi_vectors):
    module1_vectors = [lsi_vectors[key]
                       for key in lsi_vectors.keys() if key.split('.')[0] == module1]
    module2_vectors = [lsi_vectors[key]
                       for key in lsi_vectors.keys() if key.split('.')[0] == module2]

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
    vectorizer = TfidfVectorizer(sublinear_tf=True, use_idf=True, stop_words=None, smooth_idf=True)
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


# andles input to this script
def init_arg_parser():
    parser = argparse.ArgumentParser(description="CCBM calculator")
    parser.add_argument(
        "path", help="Directory where student assignment is stored (absolute path)")
    parser.add_argument("dimension", nargs='?',
                        help="Dimensions to reduce lsi vectors to, default=100", default=100, type=int)
    return parser.parse_args()


def main():
    args = init_arg_parser()

    path = args.path

    dimension = args.dimension

    files_in_dir = ICP.retrieve_files_in_dir(path)

    module_names_in_dir = [file_name.split(
        '/')[-1].split('.py')[0] for file_name in files_in_dir]

    modules_source_code = retrieve_source_code(files_in_dir, module_names_in_dir)

    lsi_vectors = retrieve_lsi_vectors(modules_source_code, dimension)

    ccbm_scores = compute_ccbm_scores(module_names_in_dir, lsi_vectors)

    generate_feedback.CCBM_feedback(ccbm_scores)


if __name__ == '__main__':
    main()
