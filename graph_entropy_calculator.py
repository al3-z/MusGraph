import networkx as nx
from math import log
import community
from cdlib import algorithms
import matplotlib.pyplot as plt


#a partir de una gráfica y una lista de comunidades disjuntas, calcular la entropía final de cada nodo y de la gráfica

def node_entropy_calculator(G, communities):
    entropy_dic={}
    for v in G.nodes():
        neighbors = [x for x in G.neighbors(v)]
        for com in communities:
            if v in com:
                community = com
        print("community of node {}: ".format(v), community)
        inner_neighbors=[]
        for x in community:
            if x!=v and x in neighbors:
                inner_neighbors.append(x)
        print("inner_neighbors: ", inner_neighbors , "  neighbors: ", neighbors,"\n")
        inner_p=len(inner_neighbors)/len(neighbors)
        outer_p=1-inner_p
        print("inner_p for node {}: ".format(v), inner_p, "outer_p for node {}: ".format(v), outer_p)
        if inner_p!=0 and outer_p!=0:
            e_v=-inner_p*log(inner_p,2)-outer_p*log(outer_p,2)
        elif inner_p==0:
            e_v =- outer_p * log(outer_p, 2)
        else:
            e_v = -inner_p * log(inner_p, 2)
        print("e_v for node {}: ".format(v), e_v)
        entropy_dic[v]=e_v

    return entropy_dic






def graph_entropy_calculator(entropy_dic):
    g_entropy=0.0
    for v in entropy_dic:
        g_entropy+=entropy_dic[v]
    avg_g_entropy=g_entropy/len(entropy_dic) #normalized with respect to the number of nodes in the graph

    return g_entropy, avg_g_entropy






if __name__ == "__main__":
    G=nx.karate_club_graph()
    #communities=community.community_louvain.best_partition(G) #esto usa otra libreria: community, en python-louvain; regresa un dicc que habria que transformar en lista de listas de comunidades, como lo hace cdlib
    #clustering=algorithms.louvain(G, weight='weight', resolution=1., randomize=False) #algorithms pertenece a la libreria cdlib para deteccion de comunidades; trae varios métodos
    clustering = algorithms.graph_entropy(G)
    communities=clustering.communities
    print("\ncommunities:", communities, "\n")
    entropy_dic=node_entropy_calculator(G,communities)
    print("Entropy dictionary: ")
    print( entropy_dic, "\n")
    g_entropy=graph_entropy_calculator(entropy_dic)
    print("Graph entropy: ", g_entropy[0], "Average graph entropy: ", g_entropy[1])
    nx.draw(G, with_labels=True)
    plt.show()