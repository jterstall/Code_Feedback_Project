from __future__ import division
import networkx as nx
import matplotlib.pyplot as plt

def ICP_module_feedback(ICP_module):
    if len(ICP_module) > 0:
        sorted_ICP_module = sorted(ICP_module.items(), reverse=True, key=lambda x: x[1])
        for i in range(len(sorted_ICP_module)):
            print sorted_ICP_module[i]
        create_dependency_graph(ICP_module)

def ICP_class_feedback(ICP_class):
    if len(ICP_class) > 0:
        sorted_ICP_class = sorted(ICP_class.items(), reverse=True, key=lambda x: x[1])
        for i in range(len(sorted_ICP_class)):
            print sorted_ICP_class[i]
        create_dependency_graph(ICP_class)

def create_dependency_graph(ICP):
    G=nx.DiGraph()
    for dependency, weight in ICP.iteritems():
        dependency_components = dependency.split(':')
        G.add_edge(dependency_components[0], dependency_components[1], calls=weight)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    calls = nx.get_edge_attributes(G, 'calls')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=calls)
    plt.show()

def CCBM_feedback(ccbm_scores, path):
    # with open('/home/jterstall/Documents/Afstudeerproject_AI/Code/Tool_Results/ConceptualCoupling_Results.txt', 'a') as f:
    #     f.write("\n\n\n")
    #     f.write(path.split('/')[-1])
    #     f.write("\n")
    #     for score in ccbm_scores:
    #         f.write(str(score[0]))
    #         f.write("\n")
    #         f.write(str(score[1]))
    #         f.write("\n")
    for score in ccbm_scores:
        print score[0]
        print score[1]
