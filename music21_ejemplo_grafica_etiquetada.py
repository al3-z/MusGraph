import music21 as m21
import networkx as nx
import matplotlib.pyplot as plt
score=m21.corpus.parse('schoenberg/opus19/movement2.mxl')
scoreflat=score.flat   #hay que aplanarlo para obtener lo offsets acumulados y no por compás
acs=scoreflat.chordify()
lista=[]
for n in acs.recurse().getElementsByClass('Chord'):
    lista.append([n.orderedPitchClasses, n.quarterLength, n.offset]) #en este ejemplo trabajaremos con equivalencia de octava (orderedPitchClasses)
print(lista)
print("# eventos:",len(lista))
G=nx.Graph()
for i in range(len(lista)):
    for x in lista[i][0]:
        G.add_edges_from([((x,i),(y,i)) for y in lista[i][0] if y!=x])
        if i <(len(lista)-1):
            G.add_edges_from([((x,i),(y,i+1)) for y in lista[i+1][0]])
nx.draw_networkx(G)
plt.show()
from more_itertools import windowed
from collections import Counter
nameTuples=[]
for n1,n2 in windowed(acs.recurse().notes, 2):       #lista de transiciones de acordes consecutivos
    nameTuples.append((tuple(n1.orderedPitchClasses), tuple(n2.orderedPitchClasses)))
c=Counter(tuple(nameTuples))    #contador de acordes consecutivos: es un diccionario
totalNotes=len(acs.recurse().notes)
{k: v / totalNotes for k,v in c.items()}
print(c)
print("# total de transiciones:",len(nameTuples))
print("# acordes distintos:",len(c))
print("radio:",nx.radius(G))
print("diámetro:",nx.diameter(G))
print("centro:", nx.center(G))
print("periferia:",nx.periphery(G))
