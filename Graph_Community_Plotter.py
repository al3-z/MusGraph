import networkx as nx
import matplotlib.pyplot as plt
from cdlib import algorithms


def Graph_CDLIB_Community_Plotter(G, community_CDLIB_method, title=None, printCommunities=False, color_map=None, plotSubGraphs=True, multipartite_node_color=None): #G grafica de networkX, communities una lista de comunidades
    community_method=community_CDLIB_method.method_name
    communities=community_CDLIB_method.communities
    pos=nx.spring_layout(G)
    if printCommunities==True:
        Tot=0
        for i in range(len(communities)):
            com=communities[i]
            print("community {} :".format(i), com)
            Tot+=len(com)
        print("Total sum of nodes in communities: ", Tot)
    if Tot!=G.number_of_nodes():
        print("WARNING: Communities are not disjoint")
    if color_map==None:
        color_map=[]
        found=set()
        for i in range(len(communities)):
            for v in communities[i]:
                if v not in found:
                    G.nodes()[v]["{}_community".format(community_method)]=i    #si se usan los métodos de CDLIB, que tienen el atributo method_name
                    found.add(v)
        for x in G.nodes():
            color_map.append(G.nodes()[x]["{}_community".format(community_method)])     #si se usan los métodos de CDLIB, que tienen el atributo method_name
        print("\nusing default color_map: ", color_map)
        print("length of color_map: ", len(color_map))
        print("\nNumber of nodes: ", G.number_of_nodes())
        print("\nNodes with attributes: ", G.nodes(data=True))
    nx.draw_networkx(G,pos,node_color=color_map,with_labels=True)
    plt.title("Community detection method: {}".format(community_method))
    plt.xlabel("{}".format(title))
    plt.show()
    if plotSubGraphs==True:
        for i in range(len(communities)):
            if i <5:
                community_subGraph=G.subgraph(communities[i])
                nx.draw_networkx(G.subgraph(communities[i]), node_color=multipartite_node_color)
                plt.title("p-c-i-r community #{} by {}".format(i + 1, community_method))
                plt.xlabel("{}".format(title))
                plt.tight_layout()
                plt.show()


#FALTA: un graficador de comunidades que tome listas no necesariamente producidas por un algoritmo de la librería CDLIB







if __name__ == "__main__":
    G = nx.karate_club_graph()
    titulo="Karate Club Graph"
    g_CDLIB_communities = algorithms.greedy_modularity(G)
    communities=g_CDLIB_communities.communities
    Graph_CDLIB_Community_Plotter(G, g_CDLIB_communities, title=titulo, printCommunities=True, plotSubGraphs=True)