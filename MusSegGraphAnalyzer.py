#se toman en cuenta _notas_acordes_intervalos_ritmos_sin_octavas_sin_inversiones


from MusGraphAnalyzer import MusGraphAnalyzer
import music21 as m21
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys


temp_stdout=sys.stdout


def MusSegGraphAnalyzer(file, compasInicio=0, compasFin=16, salto=4, longitud=8, showPlots=False, savePlots=False, plotEulerianPath=False, plotColumns=False, normalizeDomain=False, saveDataFrames=True, exportOutput=False):
    file=file
    score = m21.converter.parse(file)
    scoreTitle=file.rsplit('/', 1)[-1]
    score_interval_windows="bb_{0}-{1}_{2}_every_{3}".format(compasInicio,compasFin,longitud,salto)
    folder = file.rsplit('/', 1)[0] + '/'
    if exportOutput==True:
        output_file=folder+'{0}_MusSegGraphAnalyzer_console_output.txt'.format(scoreTitle[0:-4]+"_"+score_interval_windows)
        sys.stdout = open(output_file, 'w')
    print("scoreTitle: ", scoreTitle)
    print("score interval, window size and frequency: ", score_interval_windows)
    if len(score.parts)==0 or score.parts[0].hasMeasures()==False:
        score = score.measures(0,None)
    lenScore=len(score.parts[0].getElementsByClass('Measure'))
    print("número de compases: ", lenScore)
    modSalto=lenScore%salto
    print("modSalto: ", modSalto)
    if compasFin==None:
        compasFin=lenScore
    title=scoreTitle[0:-4]+" - mm. {0}-{1}".format(compasInicio, compasFin)
    if normalizeDomain==True:
        title=title+" - norm. timeline"
    print("title: ", title)
    #for i in range(0,lenScore-modSalto-salto,salto):
    for i in range(compasInicio,compasFin,salto):
        inicioFrag=i
        finFrag=i+longitud
        if longitud==1:
            print("\n\n\nCOMPÁS {0}: ".format(finFrag))
        else:
            print("\n\n\nCOMPASES {0}, {1}: ".format(inicioFrag,finFrag))
        frag=score.measures(inicioFrag,finFrag,indicesNotNumbers=True)
        score_graph_metrics = MusGraphAnalyzer(file, inicio=inicioFrag, fin=finFrag, score=frag, showPlots=showPlots, savePlots=savePlots, showEntropyPlot=False, plotEulerianPath=plotEulerianPath, exportOutput=exportOutput)
        print("score_graph_metrics: ", score_graph_metrics)
        if score_graph_metrics != None:
            items = list(score_graph_metrics.items())
            items.insert(0, ("centralBar", ((2*inicioFrag+longitud)/2)))
            score_graph_metrics_bars = dict(items)
            if i==compasInicio:
                df = pd.DataFrame.from_dict([score_graph_metrics_bars])
            else:
                if type(df)==bool:
                    df=pd.DataFrame()
                else:
                    df=df.append(score_graph_metrics_bars, ignore_index=True)
        else:
            df=False
            continue
    if df.empty==False:
        print("\n\nDataFrame:\n", df)
    else:
        print("Empty DataFrame")

    title_measure_cover = title + " ({} mm. every {})".format(longitud, salto)
    if plotColumns==True:
        DF_columnPlotter(df, xAxis="centralBar", plotSeparate=False, plotTogether=True, title=title_measure_cover, normalizeDomain=normalizeDomain)
    if saveDataFrames==True:
        folder="/Users/alberto/Documents/doc_codigo/doc_codigo_ejemplos/music21_doc/"
        CSV_filename=title_measure_cover+'.csv'
        search_CSV_file=bool(len(find_files(CSV_filename,folder)))
        if search_CSV_file==False:
            df.to_csv(CSV_filename)
        else:
            print("WARNING:   File {} already exists".format(CSV_filename))
            df.to_csv(CSV_filename, mode='a', index=False, header=False)

    if exportOutput == True:
        sys.stdout.close()
    return df



def DF_columnPlotter(df, xAxis=None, plotSeparate=False, plotTogether=True, title=None, normalizeDomain=False):
    if normalizeDomain==True:
        df["centralBar"]=df["centralBar"]/df["centralBar"].iat[-1]
    if plotSeparate == True:
        for column in df:
            if column != xAxis:
                df.plot(kind='line', x=xAxis, y=columnm, title=title)

                #plt.savefig(dest)  # write image to file
                plt.show()
                #plt.cla()
    if plotTogether==True and df.empty==False:
        num_plots=len(df.columns)-1
        ax = plt.gca()
        lineTypes=['-', '--', ':', '-.']
        linestyleList=[]
        for i in range(num_plots):
            j=i%len(lineTypes)
            linestyleList.append(lineTypes[j])
        custom_cycler = (plt.cycler(color=plt.cm.Dark2(np.linspace(0, 1, num_plots))) + plt.cycler(linestyle=linestyleList)) #con plt.cm se elige un colormap (ver https://matplotlib.org/1.2.1/examples/pylab_examples/show_colormaps.html)
        ax.set_prop_cycle(custom_cycler)
        for column in df:
            if column != xAxis:
                df.plot(kind='line', x=xAxis, y=column, ax=ax, title=title)
            #plt.savefig(dest)  # write image to file
        #ax.set_xticks(list(df["centralBar"])) #no funciona bien cuando aparecen valores complejos no reales en los números de compases centrales de cada ventana (?? por alguna razón a veces apaerecen complejos!! ??)
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
        plt.show() #en la pantalla de la imagen, con la pantalla lo más extendida posible, ajustar los márgenes laterales para que alcance a salir la leyenda completa izq: 0.05, der: 0.75
        #en partituras más largas conviene no incluir la leyenda al momento de guardar la imagen, o bien puede incluirse la leyenda, con el margen izq. predeterminado (0.023), y el der. en 0.8
    #plt.close(fig)
    else:
        print("No events to plot.")





#Buscador de archivos
import os

def find_files(filename, search_path):
   result = []
# Wlaking top-down from the root
   for root, dir, files in os.walk(search_path):
      if filename in files:
         result.append(os.path.join(root, filename))
   return result

print(find_files("smpl.htm","D:"))






if __name__ == "__main__":
    file='/Users/alberto/Documents/doc/partituras_doc/modulation_symphonies_project/Beethoven-Symphony4-1_no_intro_no_repeat.mid'
    #'/Users/alberto/Documents/doc/partituras_doc/Gabriel_Pareyon-Cuartetos/Pareyon_Cuarteto_No3_preproc.mid'

    df=MusSegGraphAnalyzer(file, compasInicio=1, compasFin=None, salto=4, longitud=8, showPlots=False, savePlots=False, plotColumns=True, normalizeDomain=False, exportOutput=True)
    sys.stdout=temp_stdout
    print("\n\n\n")
    #print(df)