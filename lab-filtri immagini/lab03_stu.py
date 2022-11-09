# -*- coding: utf-8 -*-
"""lab03_stu.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16yWwjol-geepCYfHea_6OhglvApnSXCT

## **Elaborazione di Immagini Mediche**
### Laboratorio 3 - Filtri per medical imaging

*   Collegamento a Google Drive e importare le librerie necessarie
"""

from google.colab import drive
drive.mount('/content/drive')

import os, sys
import numpy as np
import skimage
import skimage.io as img
from skimage.color import rgb2gray
from skimage.util import random_noise
from scipy import ndimage
import matplotlib.pyplot as plt

!pip install plotly==5.3.1
import plotly.graph_objects as go
from plotly.subplots import make_subplots

"""*   Punto 1 (Lettura immagine, istogramma delle luminosità e colorbar)"""

# Lettura immagine
path = '/content/drive/MyDrive/EIM/Lab3/'
filename = 'RM_encefalo.jpg'
I = img.imread(path + filename)
#matrice 512x512x3 in formato uint8

# Convertire l'immagine in formato grayscale (se necessario) e float
I_fl = skimage.img_as_float(I)
I_gray=skimage.color.rgb2gray(I_fl)
#è necessario convertire in grayscale in modo da passare da matrice 3dimensioni 
#512x512x3 a matrice 2dimensioni 512x512


# Visualizzare l'immagine (con colorbar) ed il relativo istogramma delle luminosità
f = plt.figure(figsize=(15, 5))
ax1 = plt.subplot(1, 2, 1)
pos = plt.imshow(I_gray,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax1)
ax1.set_title('Originale image I')

ax2 = plt.subplot(1, 2, 2)
ax2.hist(I_gray.ravel(), bins=256)
ax2.set_title('Histogram of the image')
plt.show()

"""*   Punto 2 (Immagine con sovrapposto rumore gaussiano)"""

# Corrompere l'immagine con rumore gaussiano (varianza 0.02 e valor medio nullo)
J = random_noise(I_gray,mode='gaussian', mean=0, var=0.02)

# Visualizzare l'immagine (con colorbar) ed il relativo istogramma delle luminosità
f = plt.figure(figsize=(15, 5))
ax1 = plt.subplot(1, 2, 1)
pos = plt.imshow(J,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax1)
ax1.set_title('Immagine con rumore gaussiano')

ax2 = plt.subplot(1, 2, 2)
ax2.hist(J.ravel(), bins=256)
ax2.set_title('Istogramma delle luminosità')
plt.show()
#nell'immagine si nota una puntinatura
#nell'isto si nota una distribuzione circa gaussiana (con un numero alto
#di pixel bianchi o neri)

"""*   Punto 3 (Progettazione filtro per rumore gaussiano)"""

# Funzione per generare il kernel gaussiano (NON modificare)
def kernel_gauss(size, sigma):
  v = np.linspace(-(size-1)/2,(size-1)/2,size)
  x, y = np.meshgrid(v,v)
  h = np.exp(-((x**2 + y**2)/(2.0*sigma**2)))
  h = h/h.sum()
  return h

# Filtrare l'immagine con un filtro gaussiano mediante ndimage.correlate
h = kernel_gauss(9,2)
Jfilt = ndimage.correlate(J,h)

# Visualizzare l'immagine (con colorbar) ed il relativo istogramma delle luminosità
f = plt.figure(figsize=(15, 5))
ax1 = plt.subplot(1, 2, 1)
pos = plt.imshow(Jfilt,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax1)
ax1.set_title('Immagine filtrata tramite filtro gaussiano')

ax2 = plt.subplot(1, 2, 2)
ax2.hist(J.ravel(), bins=256)
ax2.hist(Jfilt.ravel(), bins=256)
ax2.set_title('Istogramma delle luminosità')
ax2.legend(['corrotta','dopo filtraggio'])
plt.show()

#si nota come dopo il filtro gaussiano, istogramma è molto simile a quello originale: filtro ok
f1 = plt.figure(figsize=(15, 5))
ax = plt.subplot(1, 2, 1)
ax.hist(I_gray.ravel(), bins=256)
ax.hist(Jfilt.ravel(), bins=256)
ax.set_title('Istogramma delle luminosità')
ax.legend(['originale','dopo filtraggio'])


# Visualizzare il kernel del filtro (codice già scritto)
fig = go.Figure()
fig.add_trace(go.Surface(z=h, showscale=True))
fig.update_layout(title='Gaussian kernel', autosize=True)
fig.show()

"""*   Punto 4 (Progettazione filtri gaussiani)"""

# Definire i kernel dei tre filtri gaussiani
h1 = kernel_gauss(3,0.5)
h2 = kernel_gauss(3,5)
h3 = kernel_gauss(15,0.5)

# Visualizzare i kernel dei tre filtri gaussiani
fig = make_subplots(rows=1, cols=3, specs=[[{'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}]])
fig.add_trace(go.Surface(z=h1, showscale=False), row=1, col=1)
fig.add_trace(go.Surface(z=h2, showscale=False), row=1, col=2)
fig.add_trace(go.Surface(z=h3, showscale=False), row=1, col=3)
fig.update_layout(title='Gaussian kernels', width=1400, height=500)
fig.show()

#applico i kernel all'immaginw
J1 = ndimage.correlate(J,h1)
J2 = ndimage.correlate(J,h2)
J3 = ndimage.correlate(J,h3)

f = plt.figure(figsize=(20,10))
ax1 = plt.subplot(2,3,1)
pos = plt.imshow(J1,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax1)
ax1.set_title('J1: kernel 3x3 con sigma=0.5')
ax2 = plt.subplot(2,3,2)
pos = plt.imshow(J2,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax2)
ax2.set_title('J2: kernel 3x3 con sigma=5')
ax3 = plt.subplot(2,3,3)
pos = plt.imshow(J3,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax3)
ax3.set_title('J3: kernel 15x15 con sigma=0.5')

ax4 = plt.subplot(2, 3, 4)
ax4.hist(J1.ravel(), bins=256)
ax4.set_title('Istogramma delle luminosità')
ax5 = plt.subplot(2, 3, 5)
ax5.hist(J2.ravel(), bins=256)
ax5.set_title('Istogramma delle luminosità')
ax6 = plt.subplot(2, 3, 6)
ax6.hist(J3.ravel(), bins=256)
ax6.set_title('Istogramma delle luminosità')
plt.show()

#rappresento istogramma sovrapposto
fig=plt.figure(figsize=(15,5))
ax = plt.subplot(1, 2, 1)
ax.hist(I_gray.ravel(), bins=256)
ax.hist(J1.ravel(), bins=256)
ax.hist(J2.ravel(), bins=256)
ax.hist(J3.ravel(), bins=256)
ax.legend(['originale','J1','J2','J3'])
ax.set_title('Istogramma a confronto')
plt.show()

#si nota che tra i kernel analizzati, hanno un effetto differente al variare di sigma 
#e delle dimensioni: serve il giusto compromesso tra sigma e dimensioni
#sigma minore=pendenza kernel minore=larghezza maggiore

#si nota che istogramma di J1 e J3 (stesso sigma) è circa lo stesso
#mentre J2 (sigma=5 e dim=3) è più simile all'originale

#sigma troppo basso (es 0.05), non ha effetto (per ogni dimensione)
#sigma alto: sembra ok
#sigma alto e dimensioni alte: isto molto stretto e lungo
#provando con stesso sigma (es 0.5) ma con dimesioni kernel molto diverse (3,27)
#si nota circa lo stesso effetto: come mai?

"""*   Punto 5 (Immagine con sovrapposto rumore speckle)"""

# Scrivere qui la funzione per generare il kernel di averaging
def kernel_avg(size):
  h=np.ones([size,size])
  h=h/(size*size)
  return h

# Corrompere l'immagine con rumore di tipo speckle
Jsp = random_noise(I_gray,mode='speckle', mean=0, var=0.05)

# Filtrare l'immagine con un filtro di averaging mediante ndimage.correlate
h = kernel_avg(5)
Jfilt = ndimage.correlate(Jsp,h)

# Visualizzare i risultati ottenuti
f = plt.figure(figsize=(10, 5))
ax1 = plt.subplot(1, 2, 1)
pos = plt.imshow(Jsp,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax1)
ax1.set_title('Immagine + rumore speckle')
ax2 = plt.subplot(1, 2, 2)
ax2.hist(Jsp.ravel(), bins=256)
ax2.set_title('Istogramma delle luminosità')
plt.show()

f1 = plt.figure(figsize=(10, 5))
ax1 = plt.subplot(1, 2, 1)
pos = plt.imshow(Jfilt,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f1.colorbar(pos,ax=ax1)
ax1.set_title('Immagine filtrata')

ax2 = plt.subplot(1, 2, 2)
ax2.hist(Jfilt.ravel(), bins=256)
ax2.hist(I_gray.ravel(), bins=256)
ax2.legend(['filtrata','originale'])
plt.show()

#si nota come l'istogramma delle luminosità è molto simile a quello originale (filtra bene)

"""*   Punto 6 (Immagine con sovrapposto rumore salt&pepper)"""

# Corrompere l'immagine con rumore di tipo salt&pepper
Js2p = random_noise(I_gray,mode='s&p')

# Filtrare l'immagine con un filtro di averaging mediante ndimage.correlate
h = kernel_avg(5)
Jfilt1 = ndimage.correlate(Js2p,h)

# Filtrare l'immagine con un filtro mediano mediante ndimage.median_filter
Jfilt2 = ndimage.median_filter(Js2p,5)

# Visualizzare i risultati ottenuti
f = plt.figure(figsize=(10, 5))
ax1 = plt.subplot(1, 2, 1)
pos = plt.imshow(Js2p,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax1)
ax1.set_title('Immagine con rumore sale e pepe')
ax2 = plt.subplot(1, 2, 2)
ax2.hist(Js2p.ravel(), bins=256)
ax2.set_title('Istogramma')
plt.show()

f1 = plt.figure(figsize=(10, 5))
ax1 = plt.subplot(1, 2, 1)
pos = plt.imshow(Jfilt1,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f1.colorbar(pos,ax=ax1)
ax1.set_title('filtrata con filtro di averaging')
ax2 = plt.subplot(1, 2, 2)
ax2.hist(Jfilt1.ravel(), bins=256)
ax2.hist(I_gray.ravel(), bins=256)
ax2.legend(['filtrata','originale'])
plt.show()

f2 = plt.figure(figsize=(10, 5))
ax1 = plt.subplot(1,2 , 1)
pos = plt.imshow(Jfilt2,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f2.colorbar(pos,ax=ax1)
ax1.set_title('filtrata con filtro mediano')
ax2 = plt.subplot(1, 2, 2)
ax2.hist(Jfilt2.ravel(), bins=256)
ax2.hist(I_gray.ravel(), bins=256)
ax2.legend(['filtrata','originale'])
plt.show()

#si nota che entrambi i filtri rimuovono i pixel bianchi e neri che sono stati 
#generati dal rumore
#sembra che filtro averaging funziona meglio perchè si ottiene un isto più simile 
#a quello reale

"""*   Punto 7 (Gradienti orizzontale e verticale utilzzando il kernel derivativo base)"""

# Definire il kernel derivativo base
hx = np.array([[1,0,-1]])
#hx = np.array([np.linspace(1,-1,3)])   #giusto
#senza le doppie parentesi quadre, vede 3 elementi separate
#con le doppie quadre, lo vede come vettore di 3 elementi
hy = np.transpose(hx)

# Ricavare i gradienti orizzontale e verticale
Jx = ndimage.correlate(I_gray,hx)
Jy = ndimage.correlate(I_gray,hy)

# Visualizzare i risultati
f = plt.figure(figsize=(10, 5))
ax1 = plt.subplot(1,2 , 1)
pos = plt.imshow(Jx,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax1)
ax1.set_title('Jx')
ax2 = plt.subplot(1,2 , 2)
pos = plt.imshow(Jy,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax2)
ax2.set_title('Jy')
plt.show()

#si nota come il gradiente lungo x (orizzontale), evidenzia le discontinuità verticali
#e quello lungo y (verticale), evidenzia quelle orizzontali

"""*   Punto 8 (Gradienti orizzontale e verticale di Sobel)"""

# Definire il kernel di Sobel
hx=np.array([1,0,-1])
hxs = np.array([hx,2*hx,hx])/4
hys = np.transpose(hxs)

# Ricavare i gradienti orizzontale e verticale
Jxs = ndimage.correlate(I_gray,hxs)
Jys = ndimage.correlate(I_gray,hys)

# Visualizzare i risultati
f = plt.figure(figsize=(10, 5))
ax1 = plt.subplot(1,2 , 1)
pos = plt.imshow(Jxs,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
# cax1=f.add_axes([ax1.get_position().x1+0.01,ax1.get_position().y0,0.02,ax1.get_position().height])
f.colorbar(pos,ax=ax1)
ax1.set_title('Jx')

ax2 = plt.subplot(1,2 , 2)
pos = plt.imshow(Jys,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
# cax2=f.add_axes([ax2.get_position().x1+0.01,ax2.get_position().y0,0.02,ax2.get_position().height])
f.colorbar(pos,ax=ax2)
ax2.set_title('Jy')
plt.show()

#non si notano particolari differenze nel concreto (ok, chiesto al ragazzo)

"""*   Punto 9 (Image Sharpening)"""

# Effettuare sharpening dell'immagine
#sommo all'immagine originale i gradienti di Sobel in direzione x e y
Ifin = I_gray + Jxs + Jys
#in alternativa posso usare np.add 2 volte
#A=np.add(I_gray,Jxs)
#B=np.add(A,Jys)

# Visualizzare i risultati
f = plt.figure(figsize=(10, 5))
ax1 = plt.subplot(1,2 , 1)
pos = plt.imshow(I_gray,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax1)
ax1.set_title('Immagine originale')
ax2 = plt.subplot(1,2 , 2)
pos = plt.imshow(Ifin,cmap=plt.cm.gray) #, norm=plt.Normalize(vmin=0,vmax=255))
f.colorbar(pos,ax=ax2)
ax2.set_title('Immagine sharpening')
plt.show()

# Conversione in uint8 e salvataggio immagine modificata
#occorre saturare i bit oltre 0 e 1 e poi convertire in uint8
Ifin[Ifin<0]=0
Ifin[Ifin>1]=1
Ifin_uint=skimage.img_as_ubyte(Ifin)

f= plt.figure(figsize=(10,5))
ax= plt.imshow(Ifin_uint,cmap=plt.cm.gray)
plt.colorbar(ax)
plt.title('Immagine in interi')

#salvataggio immagine
path='/content/drive/MyDrive/EIM/Lab3/'
img.imsave(path + "RM_encefalo_interi.jpg", Ifin_uint)