from __future__ import division
import networkx as nx
import matplotlib.pyplot as plt

def generate_feedback(CC_files, CC_classes, ICP_module, ICP_class):
    ICP_graph(ICP_class)

def ICP_graph(ICP_dict):
    if len(ICP_dict) > 0:
        G=nx.DiGraph()
        for dependency, weight in ICP_dict.iteritems():
            dependency_components = dependency.split(':')
            G.add_edge(dependency_components[0], dependency_components[1], calls=weight)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True)
        calls = nx.get_edge_attributes(G, 'calls')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=calls)
        plt.show()

def CCBM_feedback(ccbm_scores):
    for score in ccbm_scores:
        print score[0]
        print score[1]
