# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 20:35:12 2019

@author: santo
"""
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

scale=[1/np.sqrt(2),1/np.sqrt(2)] #Filtro pasa bajas
wavelet=[-1/np.sqrt(2),1/np.sqrt(2)] #Filtro pasa altas

img=cv.imread('tkd.jpg',0)
img=img/300

def filterimg(img):
  filas,columnas=img.shape
  #Filtro pasa bajas
  pasobajo=np.empty((filas,columnas+1))
  for i in np.arange(filas):
    pasobajo[i,:]=np.convolve(img[i,:],scale,'full') #Filtro pasa bajas para cada fila
  
  #Filtro pasa bajo/pasa bajo
  pasobajobajo=np.empty((int(np.ceil(filas/2))+1,columnas))
  for i in np.arange(columnas):
    pasobajobajo[:,i]=np.convolve(pasobajo[0::2,i],scale,'full') #Filtro pasa bajas para columna
  pasobajobajo=pasobajobajo[:,1::2] #Reduce la matriz 
  pasobajobajo=pasobajobajo
  #Filtro pasa bajo/pasa alto
  pasobajoalto=np.empty((int(np.ceil(filas/2))+1,columnas))
  for i in np.arange(columnas):
    pasobajoalto[:,i]=np.convolve(pasobajo[0::2,i],wavelet,'full') #Filtro pasa altas para columna
  pasobajoalto=pasobajoalto[:,1::2]
  #Filtro pasa alto
  pasoalto=np.empty((filas,columnas+1))
  for i in np.arange(filas):
    pasoalto[i,:]=np.convolve(img[i,:],wavelet,'full') #Filtro pasa altas para cada fila
  
  #Filtro pasa alto/ pasa bajo
  pasoaltobajo=np.empty((int(np.ceil(filas/2))+1,columnas))
  for i in np.arange(columnas):
    pasoaltobajo[:,i]=np.convolve(pasoalto[0::2,i],scale,'full')#Filtro pasa bajas para columna
  pasoaltobajo=pasoaltobajo[:,1::2]
  #Filtro pasa alto/ pasa alto
  pasoaltoalto=np.empty((int(np.ceil(filas/2))+1,columnas))
  for i in np.arange(columnas):
    pasoaltoalto[:,i]=np.convolve(pasoalto[0::2,i],wavelet,'full')#Filtro pasa altas para cada columna
  pasoaltoalto=pasoaltoalto[:,1::2]
  return pasobajobajo, pasobajoalto, pasoaltobajo, pasoaltoalto

def filterimglevel(img,n):
  #img---imagen a la cual se le realiza el filtro
  #n--- numero de veces que se realizara el filtro
  levels=[]
  for i in np.arange(n):
    pasobajobajo, pasobajoalto, pasoaltobajo, pasoaltoalto=filterimg(img)
    
    
    levels.append([pasobajobajo,pasobajoalto,pasoaltobajo,pasoaltoalto])
    img=pasobajobajo
  return  pasobajobajo, pasobajoalto, pasoaltobajo, pasoaltoalto,levels

n=int(input('Ingrese el número de niveles: '))

    
#pasobajobajo, pasobajoalto, pasoaltobajo, pasoaltoalto=filterimg(img)
pasobajobajo, pasobajoalto, pasoaltobajo, pasoaltoalto,levels=filterimglevel(img,n)
"""
plt.subplot(2,2,1)
plt.imshow(pasobajobajo)
plt.subplot(2,2,2)
plt.imshow(pasobajoalto)
plt.subplot(2,2,3)
plt.imshow(pasoaltobajo)
plt.subplot(2,2,4)
plt.imshow(pasoaltoalto)

plt.show()
"""

def grafLevelsimg(levels):
    levels.reverse() #Se invierte la lista para facilidad

    for i in np.arange(len(levels)):
    
        if i < len(levels)-1:
        
            filaUp=cv.hconcat([levels[i][0],levels[i][1]]) #Concatena las imagenes filtro paso bajo bajo y filtro paso bajo alto
            filaDown=cv.hconcat([levels[i][2],levels[i][3]])#Concatena las imagenes filtro paso alto bajo y filtro paso alto alto
            f1,c1=filaUp.shape 
            f2,c2=filaDown.shape
            c=min(c1,c2) 
            matriz=cv.vconcat([filaUp,filaDown[:,:c]]) #Concatena las dos imagenes obtenidas anteriormente
            filas,columnas=levels[i+1][0].shape
            filasM,columnasM=matriz.shape
            filas=min(filas,filasM)
            columnas=min(columnas,columnasM)
            levels[i+1][0]=matriz[0:filas][0:columnas] # El filtro pasa bajo bajo del nivel inmediatamente anterior se cambia por la matriz del nivle actual
            #Se busca que tanto las imagenes filtradas como nueva matriz tengan las mismas dimensiones
            levels[i+1][1]=levels[i+1][1][0:filas][0:columnas]
            levels[i+1][2]=levels[i+1][2][0:filas][0:columnas]
            levels[i+1][3]=levels[i+1][3][0:filas][0:columnas]
    
        else:#Cuando se grafica el primer nivel no se necesita que la matriz obtenida se guarde en un nivel anterio, ya que no lo hay
            filaUp=cv.hconcat([levels[i][0],levels[i][1]])
            filaDown=cv.hconcat([levels[i][2],levels[i][3]])
            f1,c1=filaUp.shape
            f2,c2=filaDown.shape
            c=min(c1,c2)
            matriz=cv.vconcat([filaUp,filaDown[:,:c]])
        
        #plt.imshow(matriz)
        cv.imshow('M',matriz)
        cv.waitKey()  


grafLevelsimg(levels)

# cap = cv.VideoCapture(0)


# while(True):
 
#     ret, frame = cap.read()
    
#     gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
#     gray=gray/250
#     #gray=gray.astype('float16')
#     filtros=filterimglevel(gray,1)
#     filaUp=cv.hconcat([filtros[0],filtros[1]])
#     filaDown=cv.hconcat([filtros[2],filtros[3]])
#     matriz=cv.vconcat([filaUp,filaDown])

#     cv.imshow('Transformada de Haar Video', matriz)
    
    
#     if cv.waitKey(1) & 0xFF == ord('q'):
#         break
# # When everything done, release the capture
# cap.release()
# cv.destroyAllWindows()

