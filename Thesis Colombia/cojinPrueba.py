# -*- coding: utf-8 -*-
"""
Created on Fri May 21 23:19:13 2021

@author: Santiago Caro
"""


import numpy as np
import matplotlib.pyplot as plt
import serial
import time 
import cv2

def leerSerial(tipo,micro,buffer):
    
    """
    "Se aceptan datos tipo ASCII y tipo bytes"
    
    Cuando es ASCII
    
    El ; indica el final del mensaje, entoces cuando llega este dato se levanta una bandera
    para poder anlizar el mensajes    
    Si llega cualquier otro dato, este se almacena en el buffer
    
    Cuando son bytes
    
    El 255 indica el mensaje del fin del buffer
    
    Necesita como entradas un micro(dispositivo conectado por serial)
    un buffer (lista)
    
    """
    
    if (tipo=="ASCII"):
        try:
            dato=micro.read().decode() #Lectura del dato serial y decodificacióm
        except UnicodeDecodeError:
            print("Mensaje corrupto")
            bandAnalizar=0
            buffer=[]
            return buffer,bandAnalizar
        if (dato==";"): 
            
            bandAnalizar=1
            return buffer,bandAnalizar
        else:
            buffer.append(dato)
            bandAnalizar=0
            return buffer,bandAnalizar
    elif (tipo=="bytes"):
        dato=int.from_bytes(micro.read(),"big")
        
        if (dato==255): 
            
            bandAnalizar=1
            return buffer,bandAnalizar
        else:
            buffer.append(dato)
            bandAnalizar=0
            return buffer,bandAnalizar



def analizarMensaje(tipo,buffer,tamMatriz):
    
    """
    Se recibe un buffer y el tamaño de la matriz del cojin y retorna una matriz con los valores
    correspondientes a la lectura de cada sensor de presión
    """
    matriz=[]
    matrizReal=[]
    sensores=[]
    msg=""
    if(tipo=="ASCII"):
        if(buffer[0]=="P" and buffer[1]==","):#Si el mensaje no comienza con la P y la "coma", significa que es incorrecto
            for i in range(2,len(buffer)): #Recorre el buffer desde la posición dos hasta el final
                
                #Si entre las posiciones 2 y el final se recibe un dato diferente a un 
                #número o a una coma, el mensaje está corrupto
                if (buffer[i]!="0" and buffer[i]!="1" and buffer[i]!="2" and buffer[i]!="3" and buffer[i]!="4" and buffer[i]!="5" and buffer[i]!="6" and buffer[i]!="7" and buffer[i]!="8" and buffer[i]!="9"and buffer[i]!=","):
                    print("Mensaje corrupto")
                    bandGraficar=0
                    return sensores, bandGraficar
                else: #Los datos del buffer se concatenan en un string
                    msg=msg+buffer[i]           
            # print(msg)
            matriz=msg.split(",") #Se crea una matriz eliminando todas las comas y dejando solo los datos númericos
        else:
            print("Mensaje corrupto")
            bandGraficar=0
            return sensores, bandGraficar
            
        for i in range(len(matriz)):#Se convierte cada elemento de la matriz en un numero tipo int
            try:
                matriz[i]=int(matriz[i])
            except :
                print("Mensaje corrupto")
                bandGraficar=0
                return sensores, bandGraficar
    if(tipo=="bytes"):
       matriz=buffer
    
  
    #Se crea una lista con los valores de cada sensor
    #si se encuentra un 0, el número siguiente indica la cantidad todal de ceros que hay de forma consecutiva
    #si se encuentra cualquier otro valor(que no esté precedido de un 0), ese sera el valor corresponiende a un sensor
    i=0
    while (i<len(matriz)): 
        
        if (matriz[i]==0):
            i+=1
            for h in range(matriz[i]):
                matrizReal.append(0)
        else:
            matrizReal.append(matriz[i])
        i+=1            

    for i in range(tamMatriz[0]): #Se añade el número de filas a la matriz de sensores
        sensores.append([])
    
    for i in range(tamMatriz[0]): #Se añade todos los elementos de la matrizReal en una matriz MxM 
        for j in range(tamMatriz[1]):
            try:
                sensores[i].append(matrizReal[tamMatriz[0]*i+j])
            except IndexError:
                bandGraficar=0
                sensores=[]
                return sensores,bandGraficar
  
    bandGraficar=1
    return sensores,bandGraficar #se envia la mariz final de sensores y se levanta la bandera para graficar

def colorearCojin(cojin,fil,col,sensores):
    
    """ Se crea cuadros de 20*20 y cada cuadro tiene el valor corresponiendete a uno de los sensores
        para que la imagen se vea más grande 
    """
    for i in range(40):
        for j in range(40):
            cojin[i+40*fil,j+40*col]=sensores[fil,col]

    return cojin


def matriz2graf(sensores,cojin):
    """ Colorea todos los puntos del cojin usando la función colorearCojin 
    """
    
    for fil in range(sensores.shape[0]):
        for col in range(sensores.shape[1]):
            cojin=colorearCojin(cojin,fil,col,sensores)
    return cojin

def saveFile(file,sensores):
    
    file.write("nueva prueba \n")
    for i in range(len(sensores)):
        for j in range(len(sensores[i])):
            file.write(str(sensores[i][j])+", ")
        file.write("\n")

def waitTime (T,inicio):
    
    while True:
        fin=time.time()
        tiempo=fin-inicio
        if (round(tiempo,4)>=T):
            bandTime=1
            inicio=time.time()
            print(tiempo)
            return bandTime,inicio



if __name__=='__main__':
    tamMatriz=(16,16) #Defiinición tamaño cojin
    cojin=np.zeros((tamMatriz[0]*40,tamMatriz[1]*40),np.uint8) #Creación de la imagen que representa al cojin
    # tipo="ASCII" #"ASCII"o "bytes"
    # microControlador=serial.Serial("COM3",115200)
  
    # #Inicialización de todos los elementos
    # buffer=[]
    # bandTime=0
    # bandAnalizar=0
    # # file=open("ejemplo1.txt","w")
    # # microControlador.write("s".encode())
    # inicio=time.time()
    
    
    # while True:
        
    #     bandTime,inicio=waitTime(1,inicio) #Definición de cada cuanto se va a enviar el dato
        
    #     if(bandTime==1):
    #         bandTime=0

    #         microControlador.write("s".encode()) #Orden para pedir al cojin que envie datos
            
    #         while (bandAnalizar==0):
    #             buffer,bandAnalizar=leerSerial(tipo,microControlador,buffer) #Llenado del buffer
    #         # print(buffer)
            
    #         bandAnalizar=0
    #         sensores,bandGraficar=analizarMensaje(tipo,buffer,tamMatriz) #Convertir el buffer en una matriz con todos los valores leidos en cada sensor del cojín
    #         buffer=[]
          
    #         if (bandGraficar==1):
    #             bandGraficar=0
    #             sen=np.zeros((16,16,3),np.uint8)
    #             sensores=np.array(sensores) #Conversion a array para poder graficar despues
    #             # saveFile(file,sensores)
                        
    #             cojin=matriz2graf(sensores,cojin) #Conviete matriz de sensores en una matriz que se puede graficar
    #             cojin=cv2.applyColorMap(cojin,6)
    #             cv2.imshow('Cojin',cojin)
                
    #             if cv2.waitKey(25) & 0xFF == ord('q'):
    #                 microControlador.close()
    #                 break
                
                
    sensores=[[0 for j in range(16)] for i in range(16)]
    for i in range(16):
        for j in range(16):
            if (i>3 and i<9 and j>5 and j<9):
                sensores[i][j]=255

    sensores=np.array(sensores)    
    cojin=matriz2graf(sensores,cojin)          
    cojin=matriz2graf(sensores,cojin) #Conviete matriz de sensores en una matriz que se puede graficar
    cojin=cv2.applyColorMap(cojin, 6)
  
    cv2.imshow('Cojin',cojin)
    
    
    
        