import networkx as nx
import matplotlib.pyplot as plt



def simplicial_complex_drawer(simp):
    G = nx.Graph()
    for i in range(len(simp)):
        for j in range(len(simp[i])):
            if j<len(simp[i])-1:
                for k in range(1,len(simp[i])-j):
                    #edge=(simp[i][j],simp[i][j+k])
                    #print(edge)
                    G.add_edge(simp[i][j],simp[i][j+k])
            #print(G.edges())
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos, node_color='yellow')
    #nx.draw_networkx_labels(G, pos, font_size=16)
    plt.show()



if __name__ == "__main__":
    simp=[(5,6,7,8,9),(9,10,11,0)]
    for i in range(len(simp)):
        simplicial_complex_drawer(simp[0:i+1])
