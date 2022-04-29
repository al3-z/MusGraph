import music21 as m21
score=m21.corpus.parse('haydn/opus74no1/movement3.mxl')
#print("Haydn Cuarteto de Cuerdas op.74 no.1 en Do Mayor, III - Minueto")
eventos=[]
#score.show()
acs=score.measures(0,60).chordify() #si no se quiere todo el score, hay que poner score.measures(a,b).chordify()
#acs.show()
for ac in acs.recurse().getElementsByClass('Chord'):
    eventos.append([ac.pitchClasses,ac.quarterLength])
print("# eventos :", len(eventos))
found=set()
for i in range(len(eventos)):
    if any([tuple(eventos[i][0]) in list(found)[j] for j in range(len(list(found)))]) == False:
        found.add((tuple(eventos[i][0]),i))
    else:
        for j in range(len(list(found))):
            if tuple(eventos[i][0]) in list(found)[j]:
                eventos[list(found)[j][1]][1] += eventos[i][1]
notasdifs=[]
found2=set()
for i in range(len(eventos)):
    if any([eventos[i][0] in notasdifs[j] for j in range(len(notasdifs))])==False:
        notasdifs.append(eventos[i])
print("# conjuntos de alturas distintos:", len(notasdifs))
notas=[]
acordes=[]
for i in range(len(eventos)):
    for n in eventos[i][0]:
        if n not in notas:
            notas.append(n)
print("# clases de altura:", len(notas),":", notas)
import networkx as nx
G=nx.Graph()
for i in range(len(eventos)):
    for n in notas:
        if (n in eventos[i][0]) & (len(eventos[i][0])>1):
            G.add_edge(n,tuple(eventos[i][0]))
print("# nodos:", len(G.nodes))
print("# aristas:", len(G.edges))
print("radio: ", nx.radius(G), "    diámetro: ", nx.diameter(G))
l,r=nx.bipartite.sets(G)
print("G conexa:", nx.is_connected(G))
import matplotlib.pyplot as plt
color=nx.bipartite.color(G)
color_dict={0:'g',1:'mediumorchid'}
nx.set_node_attributes(G,color,'bipartite')
color_list=[color_dict[i[1]] for i in G.nodes.data('bipartite')]
pos={}
pos.update((node,(1,30*index)) for index, node in enumerate(l))
pos.update((node,(2,index)) for index, node in enumerate(r))
nx.draw_networkx(G, pos=pos, node_color=color_list)
plt.show()
nx.draw_networkx(G, node_color=color_list)
plt.show()
from networkx.algorithms import community
communities=community.greedy_modularity_communities(G)
print("# comunidades:", len(communities))
#graficar cada comunidad:
#for i in range(len(communities)):
#    print("    comunidad:", i, "  radio:" , nx.radius(G.subgraph(communities[i])), "  diámetro:", nx.diameter(G.subgraph(communities[i])) ,"  # nodos:",len(communities[i]), " # aristas:", len(G.subgraph(communities[i]).edges), "  0-nodos:", [n for n in G.subgraph(communities[i]).nodes if n in notas])
#for i in range(len(communities)):
#    print("Grado total y relativo de alturas en la comunidad", i, ":")
#    for n in G.subgraph(communities[i]).nodes:
#        if n in notas:
#            print("    ",n, ":   ", G.degree(n), "  ",G.subgraph(communities[i]).degree(n), "  ",G.subgraph(communities[i]).degree(n)/G.degree(n))
#    color_lista=[color_dict[i[1]] for i in G.subgraph(communities[i]).nodes.data('bipartite')]
#    nx.draw_networkx(G.subgraph(communities[i]), node_color=color_lista)
#    plt.show()
