from MusSegGraphAnalyzer import MusSegGraphAnalyzer
import numpy as np
import dtw as dtw
import matplotlib.pyplot as plt
import pandas as pd
import os


path="/Users/alberto/Documents/doc/partituras_doc/"

fileList=["JSB-Brandenburg1-I.mid","JSB-Brandenburg2-I.mid","ALP-Graffiti1_JSB.mxl"]
inicios=[9,9,9]
longitudes=[4,4,4]
saltos=[2,2,2]
finales=[16,16,16]




def find_files(filename, search_path):
   result = []

# Wlaking top-down from the root
   for root, dir, files in os.walk(search_path):
      if filename in files:
         result.append(os.path.join(root, filename))
   return result




filePairs=[]
c=0
for i in range(len(fileList)-1):
    for j in range(i+1,len(fileList)):
        pair=(fileList[i],fileList[j])
        filePairs.append(pair)
print(filePairs)

arrDic={}

for i in range(len(fileList)):
    file=fileList[i]
    fileFull = path + file
    title = file[0:-4] + " - mm. {0}-{1}".format(inicios[i], finales[i])
    CSV_title_measure_cover = title + " ({} mm. every {}).csv".format(longitudes[i],saltos[i])
    #print("CSV_title_measure_cover: ", CSV_title_measure_cover)
    path2="/Users/alberto/Documents/doc_codigo/doc_codigo_ejemplos/music21_doc/doc_grafs"
    if bool(find_files(CSV_title_measure_cover, path2))==True:
        df=pd.read_csv(CSV_title_measure_cover)
        print("CSV FILE ALREADY EXISTS: ", CSV_title_measure_cover)
    else:
        df = MusSegGraphAnalyzer(fileFull, compasInicio=inicios[i] , compasFin=finales[i], salto=saltos[i], longitud=longitudes[i], saveDataFrames=True)
    #print("DataFrame for {}".format(file))
    print(df)
    arr=df.to_numpy()
    arrDic[file] = arr
    print(arr)



for pair in filePairs:
    query = arrDic[pair[0]]
    reference = arrDic[pair[1]]
    alignment = dtw.dtw(query, reference)
    alignment.plot()
    plt.plot(alignment.index1, alignment.index2)
    plt.show()
    plt.plot(reference)
    plt.show()
    plt.plot(alignment.index2, query[alignment.index1])
    plt.show()









