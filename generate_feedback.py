from __future__ import division

def ICP_module_feedback(ICP_module):
    if len(ICP_module) > 0:
        sorted_ICP_module = sorted(ICP_module.items(), reverse=True, key=lambda x: x[1])
        max_ICP_module = sorted_ICP_module[0][1]
        min_ICP_module = sorted_ICP_module[-1][1]
        for i in range(len(sorted_ICP_module)):
            print (sorted_ICP_module[i][0], (sorted_ICP_module[i][1] - min_ICP_module) / (max_ICP_module - min_ICP_module))

        for i in range(len(sorted_ICP_module)):
            print sorted_ICP_module[i]
        # number_of_results = 5
        # if len(sorted_ICP_module) >= number_of_results - 1:
        #     for i in range(number_of_results):
        #         print sorted_ICP_module[i]
        # else:
        #     for i in range(len(sorted_ICP_module)):
        #         print sorted_ICP_module[i]

def ICP_class_feedback(ICP_class):
    if len(ICP_class) > 0:
        print ICP_class


def CCBM_feedback(ccbm_scores):
    for i in range(len(ccbm_scores)):
        ccbm_score = ccbm_scores[i][1]
        # if ccbm_score > 0.3:
        print ccbm_scores[i][0]
        print ccbm_score
