#se toman en cuenta: _notas_acordes_intervalos_ritmos_sin_octavas_sin_inversiones


import music21 as m21
import copy
import numpy as np

import vonNeumannGraphEntropy as VNGE









def MusGraphAnalyzer(filename, inicio, fin, score=None, showScore=False, showPlots=True, savePlots=False, savePlotFolder=False, showEntropyPlot=True, plotEulerianPath=False, exportOutput=False):
    score_graph_metrics={}
    score=score
    if score==None:
        score=m21.converter.parse(filename)#NOTA: hay que quitar en el archivo .xml o .mxl, etc los pentagramas que sean de percusiones no afinadas
    inicio=inicio
    fin=fin
    titulo="{}_mm.{}-{}".format(filename.rsplit('/',1)[1][:-4],inicio,fin)
    eventos=[]
    score_measures=score.measures(inicio,fin)
    if showScore:
        score_measures.show()
    #acs=score.chordify() #esta instruccion es para considerar TODO el archivo.
    acs=score_measures.chordify() #si no se quiere todo el score, hay que poner score.measures(a,b).chordify()
    #acs.show()#hay una incongruencia entre el score original y el que genera music21. en el primer piano se recorre la primera figura.(esto aplica para el son de la noche para piano a 4 manos)
    for ac in acs.recurse().getElementsByClass('Chord'):
        eventos.append([tuple(ac.normalOrder),float(ac.quarterLength)])#aquí se quitan las repeticiones de octavas en los acordes. #en vez de ac.normalOrder, podrían ponerse las clases de altura de modo ascendente, con tuple(sorted(set(ac.pitchClasses)))
    print("\n# eventos :", len(eventos))
    if len(eventos)==0:
        return
    print(eventos)#aqui puede haber acordes repetidos. aqui habria que hacer las conexiones entre acordes y ritmos, antes de sumar las duraciones. la lista "eventos" se quedará intacta para poder contar ritmos (no sumar duraciones, lo cual se hará en la lista eventos2).
    found=set()
    eventos2=copy.deepcopy(eventos) #es necesario importar la librería copy (python)y usar la función deepcopy, pues se trata de pegar una lista de listas. se pueden usar distintos métodos para copiar listas no anidadas o listas superfluas con new_list=old_list[:] (según este método sería el más rápido)
    #pero también hay otros métodos: new_list=list(old_list), ver por ejemplo https://stackoverflow.com/questions/2612802/list-changes-unexpectedly-after-assignment-how-do-i-clone-or-copy-it-to-prevent
    for i in range(len(eventos2)):#define el conjunto found como las tuplas de acordes, sumando su duración y quitando repeticiones
        eventos2[i][0]=tuple(eventos2[i][0])
        if any([eventos2[i][0] in list(found)[j] for j in range(len(list(found)))]) == False:
            found.add((eventos2[i][0],i))
        else:
            for j in range(len(list(found))):
                if eventos2[i][0] in list(found)[j]:
                    eventos2[list(found)[j][1]][1] += eventos2[i][1] #se suman las duraciones de los acordes repetidos
    #print("eventos con duraciones totales en la primera aparición: ", len(eventos2))#falta hacer que todos los acordes iguales tengan la misma duración(??)
    #print(eventos2)#la lista eventos 2 contiene las tuplas de acordes junto con su duración total sumada la primera vez que aparece el acorde en la lista.
    from collections import Counter
    ac_counts=Counter(ac for ac, _ in eventos2) #contador (tipo de diccionario) de elementos en la primera entrada (acordes) de la lista eventos2
    for i in range(len(eventos2)):#agregar la cuenta de cada acorde
        eventos2[i].append(ac_counts[eventos2[i][0]])
    print("\neventos con duraciones totales en la primera aparición, con cuenta de ocurrencias:")
    print("# eventos2: ", len(eventos2))
    print(eventos2)



    eventos2_cons=[[(eventos2[i][0],eventos2[i+1][0]),0] for i in range(len(eventos2)-1)]
    par_counts=Counter(par for par, _ in eventos2_cons)
    l=[]
    for par in eventos2_cons:
        par[1]+=par_counts[par[0]]
        if par not in l:
            l.append(par)
    eventos2_cons=l
    print("\npares de eventos consecutivos, con cuenta de ocurrencias:")
    print(eventos2_cons)


    #crear lista sin acordes repetidos, junto con su duración total y ocurrencias totales
    acsdifs=[]
    for i in range(len(eventos2)):#obtiene lista de acordes sin repetición, junto con sus duraciones totales y repeticiones totales
        if any([eventos2[i][0] in acsdifs[j] for j in range(len(acsdifs))])==False:
            acsdifs.append(eventos2[i])
    print("\n# conjuntos de alturas (acordes) distintos con duraciones totales y cuenta de ocurrencias:", len(acsdifs))
    print(acsdifs)
    notas=[]
    acordes=[]
    intervalos={}
    intervalos_acs=[]
    ritmos=[]
    for i in range(len(eventos2)):#crea una lista con clase de altura, su duracion total y numero de ocurrencias en todos los acordes
        for n in eventos2[i][0]:
            if n not in [item[0] for item in notas]:
                dur=0
                times=0
                for j in range(len(eventos2)):
                    if n in eventos2[j][0]:
                        dur+=eventos2[j][1]
                        times+=eventos2[j][2]
                notas.append((n,dur,times))
    print("\n# clases de altura: ", len(notas)," : ", notas)

    for i in range(len(acsdifs)):
        intervalos_acorde=[]
        for j in range(len(acsdifs[i][0])-1):
            intervalos_acorde.append((acsdifs[i][0][j+1]-acsdifs[i][0][j])%12) #se toman los intervalos consecutivos en el vector dado (por ejemplo, forma normal); podría también hacerse tomando todos los intervalos entre todas las alturas
        intervalos_acs.append([tuple(intervalos_acorde),acsdifs[i][1],acsdifs[i][2]])
        #se agrega la duración total del acorde al que pertenecen los intervalos y el num de ocurrencias
        #NOTA: otra opcion es usar la funcion de music21: vector de intervalos
    print("\n# acordes como n-adas de intervalos con duraciones totales y cuenta de ocurrencias: ", len(intervalos_acs) , ':')
    print(intervalos_acs)

    #diccionario de intervalos por separado (no como tupla)
    for t in intervalos_acs:
        if len(t[0])>0:
            for i in t[0]:
                if i in intervalos:
                    intervalos[i][0]+=t[1]
                    intervalos[i][1]+=t[2]
                else:
                    intervalos[i]=[t[1],t[2]]

    print("\n# intervalos con duraciones totales: ", len(intervalos) , ':')
    print(intervalos)



    for i in range(len(acsdifs)):
        acordes.append(tuple((tuple(m21.chord.Chord(acsdifs[i][0]).normalOrder),acsdifs[i][1],acsdifs[i][2])))#la hacemos tupla para añadirla directamente como nodo en la grafica (hashable)
    print("\n# acordes: ", len(acordes) , ':')
    print(acordes)


    for i in range(len(eventos)):
        #print(eventos2[i][1]) #lista de duraciones totales
        if eventos[i][1] not in ritmos:#esto agrega un ritmo cada que aparece en la lista eventos, pues eventos[i][1] nunca pertenece tal cual a la lista ritmos (la lista ritmos tiene como elementos listas cuya entrada [0][0] tiene el ritmo en cuestión)
            ritmos.append([(eventos[i][1],'qL'),0])#agrega a la lista ritmos los ritmos de los acordes de la lista original, "eventos"
    #print("# ritmos: ", len(ritmos) , ':', ritmos)
    rit_counts=Counter(rit for rit, _ in ritmos)
    for i in range(len(ritmos)):#agregar a cada entrada de la lista ritmos2 el número de veces que aparece en la lista original, "eventos". así se puede obtener también la suma de duraciones de cada ritmo (lo cual es desechable, al tener en cuenta que al ser ritmos ya son duraciones).
        ritmos[i][1]=rit_counts[ritmos[i][0]]
        ritmos[i]=tuple(ritmos[i])
    ritmos=list(set(ritmos))
    print("\n# ritmos con contador: ", len(ritmos) , ':', ritmos)













    #a partir de aquí se construye la gráfica
    import networkx as nx
    import itertools
    import matplotlib.pyplot as plt
    from networkx.utils import pairwise
    G=nx.Graph()
    G.add_nodes_from([item[0] for item in notas])#acordes e intervalos no pueden agregarse con este método, pues contienen listas (unhashable), hay que hacerlas tupla primero (hashable)
    #hay que agregar las clases de alturas a partir de las primeras entradas de la lista notas, que contiene duraciones y ocurrencias totales de cada clase de altura
    for i in range(len(acordes)):
        #if len(acordes[i][0]) > 1:#esto es para sólo tener los acordes con más de una nota. OJO: habria que activarlo tambien más abajo, al momento de dibujar los nodos
            G.add_node(tuple(acordes[i][0]))
    """for i in range(len(intervalos_acs)): #esto agrega n-adas de intervalos correspondientes a cada acorde; pero lo que en realidad se quiere es generar los intervalos por separado.
        if len(intervalos_acs[i][0]) > 0:
            G.add_node((intervalos_acs[i][0],'iAc'))"""
    for key in intervalos:
        G.add_node((key,'i'))
    def Extract(lst):
        return [item[0] for item in lst]
    G.add_nodes_from(Extract(ritmos))
    subset_key=[]
    nx.set_node_attributes(G,subset_key,"subset")#para dibujar con multipartite_layout hay que poner al diccionario de nodos el atributo "subset"
    nx.set_node_attributes(G,subset_key,"node_color")
    notas_acs=[]
    notas_rit=[]
    acs_ints=[]
    totalDurNotas=0
    totalTimesNotas=0
    totalDurAcs=0
    totalTimesAcs=0
    totalTimesRit=0
    totalDegCentr=0
    totalEigenCentr = 0
    totalDurInts=0
    totalTimesInts=0
    for n in G.nodes():
        if n in [item[0] for item in notas]:
            G.nodes()[n]["subset"]=1
            G.nodes()[n]["node_color"]='c'
            G.nodes()[n]["weight"]=notas[[item[0] for item in notas].index(n)][1]#asigna la duración total de la clase de altura como peso
            G.nodes()[n]["times"]=notas[[item[0] for item in notas].index(n)][2]#asigna el número total de ocurrencias de la clase de altura como otro atributo llamado "times"
            totalDurNotas+=G.nodes()[n]["weight"]
            totalTimesNotas+=G.nodes()[n]["times"]
            for i in range(len(acordes)):
                if n in acordes[i][0]:
                    cont_notas_acs=acordes[i][0].count(n) #contar ocurrencias de la nota n en el acorde acordes[i][0]
                    notas_acs.append(((n,acordes[i][0]),cont_notas_acs*acordes[i][2]))
                    #print("cuenta notas:", n ,"en ", acordes[i][0] ,":", cont_notas_acs)
        elif any([n == tuple(acordes[m][0]) for m in range(len(acordes))])==True:
            G.nodes()[n]["subset"]=2
            G.nodes()[n]["node_color"]='magenta'
            G.nodes()[n]["weight"]=acordes[[item[0] for item in acordes].index(n)][1]#asigna duracion del acorde como peso
            G.nodes()[n]["times"]=acordes[[item[0] for item in acordes].index(n)][2]#asigna el número de repeticiones como "times"
            totalDurAcs+=G.nodes()[n]["weight"]
            totalTimesAcs+=G.nodes()[n]["times"]
            for r in ritmos:
                cont_nota_rit=eventos.count([tuple(n),r[0][0]])
                if cont_nota_rit>0:
                    print("acorde: ", n, "ritmo: ", r[0][0], "# veces: ", cont_nota_rit)
                    if (n,r[0][0],cont_nota_rit) not in notas_rit:
                        notas_rit.append((n,r[0][0],cont_nota_rit))
                #faltaria guardar este contador en la lista notas_rit y luego generar las aristas con este grosor
        #elif any([n[0] == intervalos_acs[k][0] for k in range(len(intervalos_acs))]) == True:
        #    G.nodes()[n]["subset"]=5
        #    G.nodes()[n]["node_color"]='indianred'
        elif n[1] == 'i':
            G.nodes()[n]["subset"]=3
            G.nodes()[n]["node_color"]='yellowgreen'
            G.nodes()[n]["weight"]=intervalos[n[0]][0]
            G.nodes()[n]["times"]=intervalos[n[0]][1]
            totalDurInts+=G.nodes()[n]["weight"]
            totalTimesInts+=G.nodes()[n]["times"]
            for i in range(len(intervalos_acs)):
                if len(intervalos_acs[i][0])>0:
                    if n[0] in intervalos_acs[i][0]:
                        cont_acs_ints=intervalos_acs[i][0].count(n[0])
                        acs_ints.append((n,acordes[i][0],cont_acs_ints*acordes[i][2]))
        elif any([n == ritmos[i][0] for i in range(len(ritmos))])==True: #OJO., para usar multipartite_layout, hay que etiquetar tuplas (hashable), no listas (unhashable)!!
            G.nodes()[n]["subset"]=4
            G.nodes()[n]["node_color"]='teal'
            G.nodes()[n]["times"]=ritmos[[item[0] for item in ritmos].index(n)][1]
            totalTimesRit+=G.nodes()[n]["times"]
    print("nodos: ", G.nodes(data=True))

    print("totalDurNotas=",totalDurNotas)
    print("totalTimesNotas=",totalTimesNotas)
    print("totalDurAcs=",totalDurAcs)
    print("totalTimesAcs=",totalTimesAcs)
    print("totalTimesRit=",totalTimesRit)
    print("totalDurInts=",totalDurInts)
    print("totalTimesInts=",totalTimesInts)



    #poner aristas: hay que poner contadores de número total de repeticiones por tipo de arista y agregarlo como anchura (width) (también hay un parámetro de transparencia para aristas (alpha); sería útil para otra medida de las aristas???; por ahora, sólo para diferenciar mejor las aristas en el dibujo)
    for i in range(len(notas_acs)):
        G.add_edge(notas_acs[i][0][0],notas_acs[i][0][1], width=notas_acs[i][1])
    for i in range(len(notas_rit)):
        G.add_edge(notas_rit[i][0],(notas_rit[i][1],'qL'), width=notas_rit[i][2])
    for i in range(len(acs_ints)):#aristas entre intervalos y acordes
        G.add_edge(acs_ints[i][0],acs_ints[i][1], width=acs_ints[i][2])

    print("\nG multipartita aristas:")
    print(G.edges.data(), "\n")



    #Calcular entropía (de Shannon).
    """
    NOTA: La entropía de una gráfica puede definirse de tres modos distintos equivalentes:
    la mínima información mutua entre las vars aleatorias X,Y, donde X es un vértice uniformemente distribuido y Y un conjunto independiente de vértices que contiene a X;
    el mínimo valor sobre todos los puntos del politopo envolvente de los vértices, de la suma de los productos de la probabilidad de cada vértice
    por el logaritmo del inverso de cada coordenada del punto;
    o bien como su número cromático
    La entropía así definida es un problema NP-hard.
    """
    entropiaShannonNotasDur=0
    entropiaShannonNotasTimes=0
    entropiaShannonAcsDur=0
    entropiaShannonAcsTimes=0
    entropiaShannonIntsDur=0
    entropiaShannonIntsTimes=0
    entropiaShannonRitTimes=0
    entropiaShannonDegCentr=0
    entropiaShannonEigenCentr=0

    import math
    deg_centr=nx.degree_centrality(G)
    eigen_centr=nx.eigenvector_centrality(G, max_iter=500) #hay que reajustar el parámetro max_iter (default=100), pues por el número de nodos (tamaño del vector) no siempre alcanza a converger la operación en 100 iteraciones
    for n in G.nodes():
        if n in [item[0] for item in notas]:
            G.nodes()[n]["p_dur"]=G.nodes()[n]["weight"]/totalDurNotas
            G.nodes()[n]["p_rep"]=G.nodes()[n]["times"]/totalTimesNotas
            G.nodes()[n]["deg_centr"]=deg_centr[n]
            totalDegCentr+=G.nodes()[n]["deg_centr"]
            G.nodes()[n]["eigen_centr"] = eigen_centr[n]
            totalEigenCentr += G.nodes()[n]["eigen_centr"]
            entropiaShannonNotasDur+=(-G.nodes()[n]["p_dur"]*math.log(G.nodes()[n]["p_dur"],2))
            entropiaShannonNotasTimes+=(-G.nodes()[n]["p_rep"]*math.log(G.nodes()[n]["p_rep"],2))
        elif any([n == tuple(acordes[m][0]) for m in range(len(acordes))])==True:
            G.nodes()[n]["p_dur"]=G.nodes()[n]["weight"]/totalDurAcs
            G.nodes()[n]["p_rep"]=G.nodes()[n]["times"]/totalTimesAcs
            G.nodes()[n]["deg_centr"]=deg_centr[n]
            totalDegCentr+=G.nodes()[n]["deg_centr"]
            G.nodes()[n]["eigen_centr"] = eigen_centr[n]
            totalEigenCentr += G.nodes()[n]["eigen_centr"]
            entropiaShannonAcsDur+=(-G.nodes()[n]["p_dur"]*math.log(G.nodes()[n]["p_dur"],2))
            entropiaShannonAcsTimes+=(-G.nodes()[n]["p_rep"]*math.log(G.nodes()[n]["p_rep"],2))
        elif n[1] == 'i':
            G.nodes()[n]["p_dur"]=G.nodes()[n]["weight"]/totalDurInts
            G.nodes()[n]["p_rep"]=G.nodes()[n]["times"]/totalTimesInts
            G.nodes()[n]["deg_centr"]=deg_centr[n]
            totalDegCentr+=G.nodes()[n]["deg_centr"]
            G.nodes()[n]["eigen_centr"] = eigen_centr[n]
            totalEigenCentr += G.nodes()[n]["eigen_centr"]
            entropiaShannonIntsDur+=(-G.nodes()[n]["p_dur"]*math.log(G.nodes()[n]["p_dur"],2))
            entropiaShannonIntsTimes+=(-G.nodes()[n]["p_rep"]*math.log(G.nodes()[n]["p_rep"],2))
        elif any([n == ritmos[i][0] for i in range(len(ritmos))])==True: #OJO., para usar multipartite_layout, hay que etiquetar tuplas (hashable), no listas (unhashable)!!
            G.nodes()[n]["p_rep"]=G.nodes()[n]["times"]/totalTimesRit
            G.nodes()[n]["deg_centr"]=deg_centr[n]
            totalDegCentr+=G.nodes()[n]["deg_centr"]
            G.nodes()[n]["eigen_centr"] = eigen_centr[n]
            totalEigenCentr += G.nodes()[n]["eigen_centr"]
            entropiaShannonRitTimes+=(-G.nodes()[n]["p_rep"]*math.log(G.nodes()[n]["p_rep"],2))



    for n in G.nodes():
        if n in [item[0] for item in notas]:
            G.nodes()[n]["p_centr"]=G.nodes()[n]["deg_centr"]/totalDegCentr
            entropiaShannonDegCentr+=(-G.nodes()[n]["p_centr"]*math.log(G.nodes()[n]["p_centr"],2))
            G.nodes()[n]["p_eigen_centr"] = G.nodes()[n]["eigen_centr"] / totalEigenCentr
            entropiaShannonEigenCentr += (-G.nodes()[n]["p_eigen_centr"] * math.log(G.nodes()[n]["p_eigen_centr"], 2))
        elif any([n == tuple(acordes[m][0]) for m in range(len(acordes))])==True:
            G.nodes()[n]["p_centr"]=G.nodes()[n]["deg_centr"]/totalDegCentr
            entropiaShannonDegCentr+=(-G.nodes()[n]["p_centr"]*math.log(G.nodes()[n]["p_centr"],2))
            G.nodes()[n]["p_eigen_centr"] = G.nodes()[n]["eigen_centr"] / totalEigenCentr
            entropiaShannonEigenCentr += (-G.nodes()[n]["p_eigen_centr"] * math.log(G.nodes()[n]["p_eigen_centr"], 2))
        elif n[1] == 'i':
            G.nodes()[n]["p_centr"]=G.nodes()[n]["deg_centr"]/totalDegCentr
            entropiaShannonDegCentr+=(-G.nodes()[n]["p_centr"]*math.log(G.nodes()[n]["p_centr"],2))
            G.nodes()[n]["p_eigen_centr"] = G.nodes()[n]["eigen_centr"] / totalEigenCentr
            entropiaShannonEigenCentr += (-G.nodes()[n]["p_eigen_centr"] * math.log(G.nodes()[n]["p_eigen_centr"], 2))
        elif any([n == ritmos[i][0] for i in range(len(ritmos))])==True: #OJO., para usar multipartite_layout, hay que etiquetar tuplas (hashable), no listas (unhashable)!!
            G.nodes()[n]["p_centr"]=G.nodes()[n]["deg_centr"]/totalDegCentr
            entropiaShannonDegCentr+=(-G.nodes()[n]["p_centr"]*math.log(G.nodes()[n]["p_centr"],2))
            G.nodes()[n]["p_eigen_centr"] = G.nodes()[n]["eigen_centr"] / totalEigenCentr
            entropiaShannonEigenCentr += (-G.nodes()[n]["p_eigen_centr"] * math.log(G.nodes()[n]["p_eigen_centr"], 2))

    print("nodos: ", G.nodes(data=True))
    print("\n Entropía de Shannon de Notas c.r. a la duración: ",entropiaShannonNotasDur)
    print(" Entropía de Shannon de Notas c.r. a las repeticiones: ",entropiaShannonNotasTimes)
    print("\n Entropía de Shannon de Acordes c.r. a la duración: ",entropiaShannonAcsDur)
    print(" Entropía de Shannon de Acordes c.r. a las repeticiones: ",entropiaShannonAcsTimes)
    print("\n Entropía de Shannon de Ritmos (c.r. a las repeticiones): ",entropiaShannonRitTimes)
    print("\n Entropía de Shannon c.r. a la centralidad de grado: ",entropiaShannonDegCentr)



    #Calcular entropía de von Neumann de la gráfica pcir

    A = nx.to_numpy_array(G)
    pcirVNGE_exact=VNGE.VNGE_exact(A)
    #pcirVNGE_approx=VNGE.VNGE_FINGER(A)
    print("Entropía de von Neumann de la gráfica pcir: (exacta / aprox.): ", pcirVNGE_exact)
    #print("Entropía aproximada de von Neumann de la gráfica pcir: ", pcirVNGE_approx)














    """from cdlib import algorithms, viz
    entropiaCDLib = algorithms.graph_entropy(G) #esta funcion nos da un objeto de tipo NodeClustering
    print("\n Entropía de gráfica según CDLib: ", entropiaCDLib)
    coms = algorithms.louvain(G)
    pos = nx.spring_layout(G)
    viz.plot_network_clusters(G, coms, pos)"""

    #import networkqit as nq
    from networkqit.infotheory.density import entropy
    from networkqit import graph_laplacian

    plt.style.use('ggplot')
    beta_range = np.logspace(-3, 3, 200)
    Sbeta = entropy(L=graph_laplacian(A),beta_range=beta_range)
    plt.semilogx(beta_range, Sbeta)
    plt.xlabel('$\\beta$')
    plt.ylabel('$S$')
    plt.title('Unnormalized spectral entropy')
    if showEntropyPlot:
        plt.show()
    if savePlots==True:
        if savePlotFolder==False:
            plt.savefig("{}-Unnormalized_spectral_entropy.png".format(titulo))
        else:
            plt.savefig(savePlotFolder+"{}-Unnormalized_spectral_entropy.png".format(titulo))
    plt.clf()

    score_graph_metrics["pitch duration entropy"]=entropiaShannonNotasDur
    score_graph_metrics["pitch occurrence entropy"]=entropiaShannonNotasTimes
    score_graph_metrics["chord duration entropy"]=entropiaShannonAcsDur
    score_graph_metrics["chord occurrence entropy"]=entropiaShannonAcsTimes
    score_graph_metrics["rhythm values entropy"]=entropiaShannonRitTimes
    score_graph_metrics["degree centrality entropy"]=entropiaShannonDegCentr
    score_graph_metrics["eigenvector centrality entropy"] = entropiaShannonEigenCentr

    score_graph_metrics["von Neumann entropy"]=pcirVNGE_exact
    #score_graph_metrics["entropiaVonNeumannAprox"]=pcirVNGE_approx

    #score_graph_metrics["entropiaGraficas"] = entropiaGraficas

    """
    #Verificar que las distribuciones de probabilidad en realidad sumen 1: (en efecto suman 1)
    suma=0
    for n in G.nodes():
        suma+=G.nodes()[n]["p_centr"]
    print("Suma de centralidades: ", suma)
    suma2=0
    suma3=0
    suma4=0
    for n in G.nodes():
        if n in [item[0] for item in notas]:
            suma2+=G.nodes()[n]["p_rep"] #cambiar tambien por p_dur
        elif any([n == tuple(acordes[m][0]) for m in range(len(acordes))])==True:
            suma3+=G.nodes()[n]["p_rep"] #cambiar tambien por p_dur
        elif any([n == ritmos[i][0] for i in range(len(ritmos))])==True: #OJO., para usar multipartite_layout, hay que etiquetar tuplas (hashable), no listas (unhashable)!!
            suma4+=G.nodes()[n]["p_rep"] #recuerda que los ritmos NO tienen atributo de duracion (sólo repeticiones)
    print("Suma notas: ", suma2)
    print("Suma acordes: ", suma3)
    print("Suma ritmos: ", suma4)
    """

    #print("notas_acs: ",notas_acs)
    #print("notas_rit: ",notas_rit)





    pos=nx.multipartite_layout(G, scale=10) #regresa un dicc de la forma {nodo: array([x,y])}, donde [x,y] indica la posición del nodo
    print('\nDiccionario de posiciones:\n',pos)
    #array_op=lambda x: np.array([x[0],x[1]*100]) #OJO: al parecer, reescalar todas las posiciones en una coordenada no funciona, pues al dibuajar la gráfica se reescala el eje (se ve igual aunque sí cambie el valor numérico de la segunda coordenada)
    #pos = {p:array_op(pos[p]) for p in pos}

    for n in pos: #cambiamos las segundas coordenadas, según la clase del nodo
        if type(n)==int: #pitch classes
            pos[n][1]=pos[n][1]*4
        elif len(n)>1 and n[1]=='qL': #ritmos
            pos[n][1]=pos[n][1]*10
        elif len(n)>1 and n[1]=='i': #intervalos
            pos[n][1]=pos[n][1]*7
        else: #acordes / n-adas de intervalos (serán el mismo número)
            pos[n][1]=pos[n][1]*2
    print('\nDiccionario de posiciones modificado:\n',pos)

    colores_nodos=[]

    for n in G.nodes():#crea lista de colores, según la clave que ya se puso antes
        colores_nodos.append(G.nodes()[n]["node_color"])
    nx.draw_networkx(G,pos,node_color=colores_nodos)
    plt.title("p-c-i-r graph")
    plt.xlabel("{}".format(titulo))
    plt.autoscale(False)
    plt.tight_layout()
    if showPlots == True:
        plt.show()
    if savePlots==True:
        if savePlotFolder == False:
            plt.savefig("{}-pcir_graph.png".format(titulo))
        else:
            plt.savefig(savePlotFolder+"{}-pcir_graph.png".format(titulo))
    plt.clf()

    #quit()

    #nx.draw_networkx_nodes(G,pos,nodelist=[item[0] for item in notas],node_color='springgreen',node_size=[50*item[1] for item in notas],alpha=0.5)#esta instrucción dibuja los nodos de la lista "notas" (pitch classes), asignando un tamaño según su duración total, y con una transparencia (alpha) constante
    A=0#suma del total de ocurrencias de notas individuales (puede ser más que el número total de eventos, pues pueden aparecer repetidas en un mismo "evento" (acorde)). Esto lo calculamos para obtener transparencias entre 0 y 1 (único rango aceptable para el parámetro alpha (transparencia)) al dividir entre A el número de ocurrencias de cada nota
    for i in range(len(notas)):
        A+=notas[i][2]
    #print("A= ", A)

    NumTotIntervalos=0
    for i in intervalos:
        NumTotIntervalos+=intervalos[i][1]


    for i in range(len(notas)):
        nx.draw_networkx_nodes(G,pos,nodelist=[notas[i][0]],node_color='springgreen',node_size=[50*notas[i][1]],alpha=notas[i][2]/A)
    for i in range(len(acordes)):
        #if len(acordes[i][0]) > 1:
            nx.draw_networkx_nodes(G,pos,nodelist=[acordes[i][0]],node_color='red',node_size=[1000*acordes[i][1]],alpha=acordes[i][2]/len(eventos))
    for i in intervalos:
        print("intervalos[{}][1]: ".format(i), intervalos[i][1], "len(eventos): ", len(eventos))
        nx.draw_networkx_nodes(G,pos,nodelist=[(i,'i')],node_color='purple',node_size=[100*intervalos[i][0]],alpha=intervalos[i][1]/NumTotIntervalos) #OJO: intervalos es un diccionario cuyas claves tienen un valor que es una lista con dos entradas: dur total y ocurrencias
    for i in range(len(ritmos)):#para asignar distintos grados de transparencia en el color de los nodos (parámetro alpha (float)), hay que asignarlo nodo por nodo (no admite listas como node_color o node_size)
        nx.draw_networkx_nodes(G,pos,nodelist=[ritmos[i][0]],node_color='blue',node_size=[50*ritmos[i][1]],alpha=ritmos[i][1]/len(eventos))
    nx.draw_networkx_labels(G,pos)
    nx.draw_networkx_edges(G,pos)
    plt.title("weighted p-c-i-r graph")
    plt.xlabel("{}".format(titulo))
    plt.tight_layout()
    if showPlots == True:
        plt.show()
    if savePlots==True:
        if savePlotFolder == False:
            plt.savefig("{}-weighted_pcir_graph.png".format(titulo))
        else:
            plt.savefig(savePlotFolder+"{}-weighted_pcir_graph.png".format(titulo))
    plt.clf()
    #asignar pesos a nodos: generar contador de alturas, acordes, intervalos y duraciones
    #asignar pesos a aristas




    #Construccion de las Graficas de Notas, Acordes, Intervalos y Ritmos
    GNotas=nx.Graph()
    GAcs=nx.DiGraph()
    GInts=nx.Graph()
    GRit=nx.DiGraph()


    colores_nodos_notas=[]
    aristas_notas=[]

    aristas_acs=[]
    aristas_ints=[]
    aristas_rit=[]

    for n in G.nodes():
        if G.nodes()[n]["subset"] == 1: #se une cada clase de altura con otra si ambas pertenecen a un mismo acorde
            GNotas.add_node(n)
            colores_nodos_notas.append(G.nodes()[n]["node_color"])
            for edge in G.edges():
                if n in edge:
                    i=1-edge.index(n)
                    for x in G.neighbors(edge[i]):
                        if G.nodes()[x]["subset"]==1:
                            aristas_notas.append((n,x))
                            GNotas.add_edge(n,x)

        elif G.nodes()[n]["subset"] == 3:
            GInts.add_node(n)
            for j in range(len(intervalos_acs)):
                if len(intervalos_acs[j][0])>0 and n[0] in intervalos_acs[j][0]:
                    for y in intervalos_acs[j][0]:
                        if y != n[0]:
                            GInts.add_edge(n,(y,'i'))
        elif G.nodes()[n]["subset"] == 4:
            GRit.add_node(n) #FALTA agregar flechas entre ritmos sucesivos
    print("\n aristas_notas: ",aristas_notas)
    print("\n aristas_intervalos: ", GInts.edges())



    GAcs.add_weighted_edges_from([(par[0][0],par[0][1],par[1]) for par in eventos2_cons])
    #print("GAcs nodos: " , GAcs.nodes(data=True))
    print("\nOrden y tamaño gráfica de acordes: ", len(GAcs.nodes()), "nodos , ", len(GAcs.edges()), " aristas")

    #agregar peso a las aristas
    for e in GNotas.edges():
        GNotas.edges()[e]['width']=aristas_notas.count(e)
    print("\nAristas GNotas: ", GNotas.edges(data=True))
    width_notas=[GNotas[u][v]['width']/2 for u,v in GNotas.edges()]
    pos=nx.shell_layout(GNotas)

    for i in range(len(notas)):
        nx.draw_networkx_nodes(GNotas,pos,nodelist=[notas[i][0]],node_color='red',node_size=[100*notas[i][1]],alpha=notas[i][2]/A)
    nx.draw_networkx_labels(GNotas,pos)
    nx.draw_networkx_edges(GNotas,pos, width=width_notas)
    plt.title("Vertical pitch class graph")
    plt.xlabel("{}".format(titulo))
    plt.tight_layout()
    if showPlots == True:
        plt.show()
    if savePlots==True:
        if savePlotFolder == False:
            plt.savefig("{}-vertical_pitch_class_graph.png".format(titulo))
        else:
            plt.savefig(savePlotFolder+"{}-vertical_pitch_class_graph.png".format(titulo))
    plt.clf()


    if len(eventos2_cons)>0:
        GNotas2=nx.DiGraph()

        GNotas2_edge_width=[]
        for par in eventos2_cons:
            for n in par[0][0]:
                GNotas2.add_weighted_edges_from([(n,k,par[1]) for k in par[0][1]])
                GNotas2_edge_width.append(par[1]*0.5) #se puede ajustar el grosor de las aristas dependiendo de la pieza
        pos=nx.shell_layout(GNotas2)

        for i in range(len(notas)):
            nx.draw_networkx_nodes(GNotas2,pos,nodelist=[notas[i][0]],node_color='turquoise',node_size=[100*notas[i][1]],alpha=notas[i][2]/A)

        nx.draw_networkx_labels(GNotas,pos)
        nx.draw_networkx_edges(GNotas2,pos,width=GNotas2_edge_width)
        plt.title("Horizontal pitch class graph")
        plt.xlabel("{}".format(titulo))
        plt.tight_layout()
        if showPlots == True:
            plt.show()
        if savePlots==True:
            if savePlotFolder == False:
                plt.savefig("{}-horizontal_pitch_class_graph.png".format(titulo))
            else:
                plt.savefig(savePlotFolder+"{}-horizontal_pitch_class_graph.png".format(titulo))
        plt.clf()




        pos=nx.circular_layout(GAcs)
        nx.draw_networkx_labels(GAcs,pos)
        nx.draw_networkx_edges(GAcs,pos, width=[2*par[1] for par in eventos2_cons])
        plt.title("Chord graph")
        plt.xlabel("{}".format(titulo))
        plt.tight_layout()
        if showPlots == True:
            plt.show()
        if savePlots==True:
            if savePlotFolder == False:
                plt.savefig("{}-chord_graph.png".format(titulo))
            else:
                plt.savefig(savePlotFolder+"{}-chord_graph.png".format(titulo))
        plt.clf()



    pos=nx.shell_layout(GInts)
    nx.draw_networkx_labels(GInts,pos)
    nx.draw_networkx_edges(GInts,pos, width=[1 for i in range(len(GInts.edges()))]) #falta poner el ancho de las aristas como un contador de ocurrencias
    plt.title("Interval graph")
    plt.xlabel("{}".format(titulo))
    plt.tight_layout()
    if showPlots == True:
        plt.show()
    if savePlots==True:
        if savePlotFolder == False:
            plt.savefig("{}-interval_graph.png".format(titulo))
        else:
            plt.savefig(savePlotFolder+"{}-interval_graph.png".format(titulo))
    plt.clf()




    """
    nx.draw_networkx(GNotas,pos=nx.shell_layout(GNotas),node_color=colores_nodos_notas)#esta ya se dibujó arriba
    plt.show()
    
    nx.draw_networkx_labels(GRit,pos)
    nx.draw_networkx_edges(GRit,pos)
    plt.tight_layout()
    plt.show()
    """
    pcirDensity=nx.density(G)
    print("\nDensidad de la gráfica de alturas-acordes-intervalos-ritmos: ", pcirDensity)
    score_graph_metrics["pcir graph density"]=pcirDensity
    pcirAvgClust=nx.average_clustering(G)
    print("\nAglomeración promedio (average clustering) de la gráfica de alturas-acordes-intervalos-ritmos: " , pcirAvgClust) #agregar nx.eccentricity, nx.shortest_path_length??
    score_graph_metrics["pcir avg clustering"] = pcirAvgClust

    # Análisis de Comunidades.

    from networkx.algorithms import community






    #Comunidades de alturas-acordes-ritmos
    
    color_dict={1:'g',2:'mediumorchid',3:'r',4:'b'}
    communities=community.greedy_modularity_communities(G) #para correr correctamente esta función, se necesita networkx 2.5 o 2.4; en 2.6 parece generar error al comparar los nodos de elementos de la gráfica multipartita que contienen entradas de diferente tipo: int, tuple, str; en el módulo MappedQueue. Sin embargo, si todos los nodos son del mismo tipo, la función (en la v 2.6) corre bien (o sea, en las gráficas de alturas o acordes).
        #parámetros de greedy_modularity_communities: resolution, best_n, cutoff, weight
                    #resolution: float, optional (default=1) If resolution is less than 1, modularity favors larger communities. Greater than 1 favors smaller communities.
    print("# comunidades:", len(communities))
    score_graph_metrics["#communities"]=len(communities)
    score_graph_metrics["modularity"]=community.modularity(G,communities)

    #graficar cada comunidad:
    for i in range(len(communities)):
        print("    comunidad:", i+1, "  radio:" , nx.radius(G.subgraph(communities[i])), "  diámetro:", nx.diameter(G.subgraph(communities[i])) ,"  # nodos:",len(communities[i]), " # aristas:", len(G.subgraph(communities[i]).edges), "  0-nodos:", [n for n in G.subgraph(communities[i]).nodes if G.nodes()[n]["subset"]==1])
    for i in range(len(communities)):
        print("\nGrado total y relativo de alturas en la comunidad", i+1, ":")
        for n in G.subgraph(communities[i]).nodes:
            if G.nodes()[n]["subset"]==1:
                print("    ",n, ":   ", G.degree(n), "  ",G.subgraph(communities[i]).degree(n), "  ",G.subgraph(communities[i]).degree(n)/G.degree(n))


        color_lista = [color_dict[j[1]] for j in G.subgraph(communities[i]).nodes.data("subset")]
        nx.draw_networkx(G.subgraph(communities[i]),node_color=color_lista)
        plt.title("p-c-i-r community #{}".format(i+1))
        plt.xlabel("{}".format(titulo))
        plt.tight_layout()
        if showPlots == True:
            plt.show()
        if savePlots == True:
            if savePlotFolder == False:
                plt.savefig("{}-pcir_community_{}.png".format(titulo, i+1))
            else:
                plt.savefig(savePlotFolder+"{}-pcir_community_{}.png".format(titulo, i + 1))
        plt.clf()





    # Graph entropy y comunidades por graph entropy
    from cdlib import algorithms, viz
    g_entropy_communities=algorithms.graph_entropy(G)

    from graph_entropy_calculator import node_entropy_calculator, graph_entropy_calculator
    entropy_dic = node_entropy_calculator(G, g_entropy_communities.communities)
    g_entropy_values=graph_entropy_calculator(entropy_dic)
    score_graph_metrics["avg graph entropy"]=g_entropy_values[1]
    print("\nEntropía de gráfica de G: ", g_entropy_values[0])
    print("Entropía de gráfica promedio de los nodos de G: ", g_entropy_values[1],"\n")

    print("\n Comunidades por entropía de gráfica: ")
    for x in g_entropy_communities.communities:
        print(x)
    """
    if showPlots == True:
        pos = nx.spring_layout(G)
        viz.plot_network_clusters(G, g_entropy_communities, pos, figsize=(5, 5))  #plot_network_clusters no puede manejar nodos on distintas dimensiones (usa la función concatenate para arrays de numpy, la cual requiere que los inputs tengan la misma forma)
    """


    from Graph_Community_Plotter import Graph_CDLIB_Community_Plotter

    if showPlots == True:
        Graph_CDLIB_Community_Plotter(G, community_CDLIB_method=g_entropy_communities, title=titulo, printCommunities=True)


    #Comunidades por máxima modularidad
    greedy_mod_communities=algorithms.greedy_modularity(G)
    if showPlots==True:
        Graph_CDLIB_Community_Plotter(G, community_CDLIB_method=greedy_mod_communities, title=titulo, printCommunities=True)

    #Comunidades por Girvan-Newman
    """girvan_newman_communities = algorithms.girvan_newman(G,level=4) #Genera ERROR!!!! si hay sólo una comunidad al parecer.
    if showPlots == True:
        Graph_CDLIB_Community_Plotter(G, community_CDLIB_method=girvan_newman_communities, title=titulo, printCommunities=True)"""

    #Comunidades de alturas verticales
    vertPitchAvgClust=nx.average_clustering(GNotas)
    print("\nAglomeración promedio (average clustering) de clases de alturas verticales: " , vertPitchAvgClust) #agregar nx.eccentricity, nx.shortest_path_length??
    print("Densidad de la gráfica de clases de alturas verticales: ", nx.density(GNotas))
    GNotass=GNotas.to_undirected() #el algoritmo de deteccion de comunidades de Networkx parece no funcionar con graficas dirigidas. para hacer deteccion de comunidades en graficas dirigidas, ver las librerias Infomap y OSLOM
    communities_vpc=community.greedy_modularity_communities(GNotass)
    print("\n# comunidades_acs:")#, len(communities_acs)
    #graficar cada comunidad:
    for i in range(len(communities_vpc)):
        print("    comunidad_alturas_verticales:", i+1, "  radio:" , nx.radius(GNotass.subgraph(communities_vpc[i])), "  diámetro:", nx.diameter(GNotass.subgraph(communities_vpc[i])) ,"  # nodos:",len(communities_vpc[i]), " # aristas:", len(GNotass.subgraph(communities_vpc[i]).edges))
    for i in range(len(communities_vpc)):
        print("\nGrado total y relativo de acordes en la comunidad", i+1, ":")
        for n in GNotass.subgraph(communities_vpc[i]).nodes:
            print("    ",n, ":   ", GNotass.degree(n), "  ",GNotass.subgraph(communities_vpc[i]).degree(n), "  ",GNotass.subgraph(communities_vpc[i]).degree(n)/GNotass.degree(n))

        nx.draw_networkx(GNotas.subgraph(communities_vpc[i]), node_color='red')
        plt.title("Vertical pitch class community #{}".format(i+1))
        plt.xlabel("{}".format(titulo))
        plt.tight_layout()
        if showPlots == True:
            plt.show()
        if savePlots == True:
            if savePlotFolder == False:
                plt.savefig("{}-vertical_pitch_class_community{}.png".format(titulo,i+1))
            else:
                plt.savefig(savePlotFolder+"{}-vertical_pitch_class_community{}.png".format(titulo, i + 1))
        plt.clf()



    if len(eventos2_cons)>0:
        #Comunidades de alturas horizontales
        horPitchAvgClust=nx.average_clustering(GNotas2)
        print("\nAglomeración promedio (average clustering) de clases de alturas horizontales: " , horPitchAvgClust) #agregar nx.eccentricity, nx.shortest_path_length??
        print("Densidad de la gráfica de clases de alturas horizontales: ", nx.density(GNotas2))
        GNotas2s=GNotas2.to_undirected() #el algoritmo de deteccion de comunidades de Networkx parece no funcionar con graficas dirigidas. para hacer deteccion de comunidades en graficas dirigidas, ver las librerias Infomap y OSLOM
        communities_hpc=community.greedy_modularity_communities(GNotas2s)
        print("\n# comunidades_acs:")#, len(communities_acs)
        #graficar cada comunidad:
        for i in range(len(communities_hpc)):
            print("    comunidad_alturas_horizontales:", i+1, "  radio:" , nx.radius(GNotas2s.subgraph(communities_hpc[i])), "  diámetro:", nx.diameter(GNotas2s.subgraph(communities_hpc[i])) ,"  # nodos:",len(communities_hpc[i]), " # aristas:", len(GNotas2s.subgraph(communities_hpc[i]).edges))
        for i in range(len(communities_hpc)):
            print("\nGrado total y relativo de acordes en la comunidad", i+1, ":")
            for n in GNotas2s.subgraph(communities_hpc[i]).nodes:
                print("    ",n, ":   ", GNotas2s.degree(n), "  ",GNotas2s.subgraph(communities_hpc[i]).degree(n), "  ",GNotas2s.subgraph(communities_hpc[i]).degree(n)/GNotas2s.degree(n))

            nx.draw_networkx(GNotas2.subgraph(communities_hpc[i]), node_color='turquoise')
            plt.title("Horizontal pitch class community #{}".format(i+1))
            plt.xlabel("{}".format(titulo))
            plt.tight_layout()
            if showPlots == True:
                plt.show()
            if savePlots == True:
                if savePlotFolder == False:
                    plt.savefig("{}-horizontal_pitch_class_community{}.png".format(titulo,i+1))
                else:
                    plt.savefig(savePlotFolder+"{}-horizontal_pitch_class_community{}.png".format(titulo, i + 1))
            plt.clf()



        #Comunidades de acordes:
        acsAvgClust=nx.average_clustering(GAcs)
        print("\nAglomeración promedio (average clustering) de acordes: " , acsAvgClust) #agregar nx.eccentricity, nx.shortest_path_length??
        print("Densidad acordes: ", nx.density(GAcs))
        GAcs2=GAcs.to_undirected() #el algoritmo de deteccion de comunidades de Networkx parece no funcionar con graficas dirigidas. para hacer deteccion de comunidades en graficas dirigidas, ver las librerias Infomap y OSLOM
        communities_acs=community.greedy_modularity_communities(GAcs2)
        print("\n# comunidades_acs:")#, len(communities_acs)
        #graficar cada comunidad:
        for i in range(len(communities_acs)):
            print("    comunidad_acs:", i+1, "  radio:" , nx.radius(GAcs2.subgraph(communities_acs[i])), "  diámetro:", nx.diameter(GAcs2.subgraph(communities_acs[i])) ,"  # nodos:",len(communities_acs[i]), " # aristas:", len(GAcs2.subgraph(communities_acs[i]).edges))
        for i in range(len(communities_acs)):
            print("\nGrado total y relativo de acordes en la comunidad", i+1, ":")
            for n in GAcs2.subgraph(communities_acs[i]).nodes:
                print("    ",n, ":   ", GAcs2.degree(n), "  ",GAcs2.subgraph(communities_acs[i]).degree(n), "  ",GAcs2.subgraph(communities_acs[i]).degree(n)/GAcs2.degree(n))

            nx.draw_networkx(GAcs.subgraph(communities_acs[i]), node_color='orange')
            plt.title("Chord community #{}".format(i+1))
            plt.xlabel("{}".format(titulo))
            plt.tight_layout()
            if showPlots == True:
                plt.show()
            if savePlots == True:
                if savePlotFolder == False:
                    plt.savefig("{}-chord_community_{}.png".format(titulo,i+1))
                else:
                    plt.savefig(savePlotFolder+"{}-chord_community_{}.png".format(titulo, i + 1))
            plt.clf()

        """
        #Análisis de ciclos dirigidos de acordes
        ciclos_acs=[]
        for ciclo in nx.simple_cycles(GAcs):
            if len(ciclo)>1:
                ciclos_acs.append(ciclo)
        print("\nCiclos dirigidos de acordes: ", len(ciclos_acs))
        for i in range(50):
            print("Ciclo  ", i, " : ", ciclos_acs[i])
        #for ciclo in ciclos: #esto imprime todos los ciclos (pueden ser muchos (en el caso del Graffiti 1 de Luna, hay mas de 633,000!!! (aunque en los Graffitis 2 y 3 son muchos menos!))) Hay que encontrar una manera de elegir los principales (por peso de aristas)
        if len(ciclos_acs)<5:
            for x in ciclos_acs:
                nx.draw_networkx(GAcs.subgraph(x), node_color='deeppink')
                plt.tight_layout()
                plt.show()
        else:
            for i in range(5):
                nx.draw_networkx(GAcs.subgraph(ciclos_acs[i]), node_color='deeppink')
                plt.tight_layout()
                plt.show()
        """

        #Análisis de ciclos de acordes
        ciclos_acs=[]
        for ciclo in nx.cycle_basis(GAcs2):
            if len(ciclo)>1:
                peso_ciclo=0
                for e in GAcs2.subgraph(ciclo).edges():
                    peso_ciclo+=GAcs2.subgraph(ciclo).edges()[e]['weight']
                ciclos_acs.append((ciclo,peso_ciclo))
        ciclos_acs.sort(key = lambda x: x[1])
        ciclos_acs.reverse()
        #print("\nNúmero de ciclos simples de acordes: ", len(list(nx.simple_cycles(GAcs)))) #imprimir list(nx.simple_cycles(GAcs))?
        print("\nTamaño de una base de ciclos de acordes: ", len(ciclos_acs))
        print(ciclos_acs)
        peso_ciclos_acs=0
        for c in ciclos_acs:
            peso_ciclos_acs+=c[1]


        #for ciclo in ciclos: #esto imprime todos los ciclos (pueden ser muchos (en el caso del Graffiti 1 de Luna, hay mas de 633,000!!! (aunque en los Graffitis 2 y 3 son muchos menos!))) Hay que encontrar una manera de elegir los principales (por peso de aristas)
        if len(ciclos_acs)<5:
            i=0

            for x in ciclos_acs:
                nx.draw_networkx(GAcs.subgraph(x[0]), node_color='deeppink')
                plt.title("Heaviest (by edges) base chord cycle #{}".format(i+1))
                plt.xlabel("{}".format(titulo))
                plt.xlabel("\nCycle weight (sum of its edges' weights) / Total weight of basic cycles: {} / {}".format(x[1],peso_ciclos_acs))
                plt.tight_layout()
                if showPlots == True:
                    plt.show()
                if savePlots == True:
                    if savePlotFolder == False:
                        plt.savefig("{}-heaviest_base_chord_cycle{}.png".format(titulo,i+1))
                    else:
                        plt.savefig(savePlotFolder+"{}-heaviest_base_chord_cycle{}.png".format(titulo, i + 1))
                plt.clf()
                i+=1
        else:

            for i in range(5):
                nx.draw_networkx(GAcs.subgraph(ciclos_acs[i][0]), node_color='deeppink')
                plt.title("Heaviest (by edges) base chord cycle #{}".format(i+1))
                plt.xlabel("{}".format(titulo))
                plt.xlabel("\nCycle weight (sum of its edges' weights) / Total weight of basic cycles: {} / {}".format(ciclos_acs[i][1],peso_ciclos_acs))
                plt.tight_layout()
                if showPlots == True:
                    plt.show()
                if savePlots == True:
                    if savePlotFolder == False:
                        plt.savefig("{} - heaviest base chord cycle #{}.png".format(titulo,i+1))
                    else:
                        plt.savefig(savePlotFolder+"{} - heaviest base chord cycle #{}.png".format(titulo, i + 1))
                plt.clf()

        #Conexidad de la grafica de acordes
        if len(acordes)>1:
            edgeConnAcs=nx.edge_connectivity(GAcs)
            print("\nConexidad por aristas de la gráfica de acordes: ", edgeConnAcs) #edge_connectivity considera el sentido de las flechas en una grafica dirigida
            #Propiedad de Euler de Acordes (Eulerianidad??)
            if edgeConnAcs>0:
                print("\nGráfica de acordes euleriana: ", nx.is_eulerian(GAcs))
                if nx.is_eulerian(GAcs):
                    c=set()
                    for e in nx.eulerian_circuit(GAcs):
                        c.update([e[0],e[1]])

                    print("   circuito euleriano: ", c )
                    nx.draw_networkx(GAcs.subgraph(c), node_color="gold")
                    plt.title("Eulerian chord circuit")
                    plt.xlabel("{}".format(titulo))
                    plt.tight_layout()
                    if plotEulerianPath == True:
                        plt.show()
                    if savePlots == True:
                        if savePlotFolder == False:
                            plt.savefig("{}-Eulerian_path.png".format(titulo))
                        else:
                            plt.savefig(savePlotFolder+"{}-Eulerian_path.png".format(titulo))
                    plt.clf()


    print("\n")

    return score_graph_metrics



if __name__ == "__main__":
    savePlotFolder='/Users/alberto/Documents/doc/2024-1/Modulation in German Classical-Romantic Sonata-Form/Haydn-Symphony1-1_plots/'
    score_graph_metrics=MusGraphAnalyzer('/Users/alberto/Documents/doc/partituras_doc/modulation_symphonies_project/Haydn-Symphony1-1.mid', inicio=46, fin=53, showPlots=True, showEntropyPlot=False, savePlots=False, savePlotFolder=savePlotFolder, exportOutput=False)
    #Indian_early_music_project/Kudumiyamalai_Inscription_Section_III.mxl
    print(score_graph_metrics)
