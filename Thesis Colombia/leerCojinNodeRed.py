# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 22:44:21 2021

@author: Santiago Caro
"""

import  cojinPrueba as cj
import numpy as np
import matplotlib.pyplot as plt
import cv2
name="suj1Cojin"

file=open(f"Pruebas mahavir\{name}.txt","r")
tamMatriz=(16,16)
#Matriz de matrices(i,j,k) 
#i= numero de matrices
#j= numero de filas de cada matriz
#k= número de columnas de cada matriz
matrices=file.readlines()

# matrices1=np.array(matrices)
for i in range(len(matrices)):
    matrices[i]=matrices[i].split("[[")[1]
    matrices[i]=matrices[i].split("]]\n")[0]
    matrices[i]=matrices[i].split("],")
    
    for j in range(len(matrices[i])):
        if (matrices[i][j].find("[")!=-1):
            matrices[i][j]=matrices[i][j].split("[")[1]
        
        matrices[i][j]= matrices[i][j].split(",") #Eliminar comas y convertir en lista
        
        for k in range(len(matrices[i][j])):
            matrices[i][j][k]=int(matrices[i][j][k]) #Conversión de todos los elementos de str a int


#Conversión de matriz a array para hacer graficación
sensores=np.array(matrices)
#Creación de matriz que se graficará
cojin=np.zeros((tamMatriz[0]*40,tamMatriz[1]*40),np.uint8) 
# cojin=cj.matriz2graf(sensores[10],cojin) #Muestra el cojin en un solo momento

#Hacer video de toda la prueba
size=cojin.shape
out = cv2.VideoWriter(f"Pruebas mahavir\{name}.avi",cv2.VideoWriter_fourcc(*'XVID'), 1, size) 
# sensores[0]
for sens in sensores:
    cojin=np.zeros((tamMatriz[0]*40,tamMatriz[1]*40),np.uint8) 
    cojin=cj.matriz2graf(sens,cojin) #Conversión a matriz para graficar cada dato en en 40*40pixeles
    cojin=cv2.applyColorMap(cojin,6) 
    out.write(cojin)

out.release()

# cojin=cv2.applyColorMap(cojin,6)
# cv2.imshow('Cojin',cojin)

    
