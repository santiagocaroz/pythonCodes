# -*- coding: utf-8 -*-
"""lab04.ipynb

"""

#%%
import os
import sys
import skimage.io as img
import matplotlib.pyplot as plt
import numpy as np
import skimage
import plotly.express as px
from skimage.color import rgb2gray
#%%

path = ''
filename = 'fegato.jpg'    
I = img.imread(path+filename)  # uint8
I_float = skimage.img_as_float(I)
I_gray = skimage.color.rgb2gray(I_float)


# %whos 
print(f"Dimensioni immagine: {I_gray.shape}")

# Visualizzare l'immagine (con colorbar)
fig = plt.figure(figsize=(15, 5))
ax1 = plt.subplot(1, 2, 1)
z1_plot = ax1.imshow(I, cmap=plt.cm.gray)
fig.colorbar(z1_plot,ax=ax1)
ax1.set_title('Immagine Originale')
ax2 = plt.subplot(1, 2, 2)
z2_plot = ax2.imshow(I_gray, cmap=plt.cm.gray)
fig.colorbar(z2_plot,ax=ax2)
ax2.set_title('Immagine grayscale')

plt.show()
#%%

#Leggere l'immagine binaria che contiene la segmentazione manuale del fegato

filename = 'fegato_mask.png'    
mask = img.imread(path + filename)  # maschera in uint8

fig = plt.figure()
ax1 = plt.subplot(1,1,1)
z1_plot = ax1.imshow(mask, cmap=plt.cm.gray)
fig.colorbar(z1_plot,ax=ax1)
ax1.set_title('Maschera della segmentazione manuale - Fegato')
fig.show()
#%%
# Trasformare in formato boolean
maskBool = np.array(mask, dtype=bool)
# Applicare la maschera sull'immagine
I_mask = I_gray*maskBool

# Visualizzare l'immagine con
fig = px.imshow(I_mask,color_continuous_scale='gray')
fig.show()

#%%

# Definire le soglie Seed e Growing 
T1 = 0.5   #Valori di soglia per i seed iniziali 
T2 = 0.44    #Valore di soglia per la crescita 


seeds_r, seeds_c = np.where(I_mask>=T1)    

maskSeeds = np.zeros(I_mask.shape)
maskSeeds[seeds_r, seeds_c] = 1

fig = px.imshow(maskSeeds,color_continuous_scale='gray')
fig.show()
#%%

ToProcess = np.ravel_multi_index((seeds_r, seeds_c), maskSeeds.shape)

# Inizializzare la maschera che conterrà la segmentazione dei vasi
K2 = np.zeros(I_mask.shape)



def conneigh8(x,y,shape):   # neigh8_x, neigh8_y = conneigh8(seeds_r,seeds_c,I.shape) 

  Nrows = shape[0]
  Ncols = shape[1]
  neigh8_x = np.array([], dtype = "uint8")
  neigh8_y = np.array([], dtype = "uint8")
  # Controllare i bordi
  for i in np.linspace(-1,1,3):
    for j in np.linspace(-1,1,3):
     if ((x+i)<Nrows and (x+i)>=0 and (y+j)<Ncols and (y+j)>=0):
       if (i== 0 and j==0):
         pass
       else:
        neigh8_x = np.append(neigh8_x, int(x+i))
        neigh8_y = np.append(neigh8_y, int(y+j))
  
  return neigh8_x, neigh8_y  #restituisce gli indici dell’insieme 8-connesso


# REGION GROWING semplificata 


while (len(ToProcess)>0):

  # Isolare un pixel da analizzare nel vettore ToProcess (ad esempio il primo)
  current = ToProcess[-1]  # ultimo valore per ogni iterazione 
  
  # Ottenere gli indici r e c dall'indice lineare (np.unravel_index)
  current_r ,current_c = np.unravel_index(current,I_mask.shape)   # restituisce index_col e index_row

  # Aggiornare la maschera di segmentazione
  K2[current_r, current_c] = 1

  # Trovare l'8-connesso del pixel analizzato con la funzione conneigh8
  n8_x, n8_y = conneigh8(current_r,current_c,K2.shape)

  # Trovare quali elementi dell'8 connesso soddisfano le seguenti due condizioni:
  # - superano la soglia di crescita T2

  # - non sono ancora stati analizzati (i.e., i pixel sono ancora pari a 0 nella 
  #   maschera di segmentazione)
  n8r_T2, n8c_T2 = np.where((I_mask[n8_x,n8_y]>=T2) & (K2[n8_x,n8_y]==0), [n8_x, n8_y], -1)  

  n8c_T2=n8c_T2[np.where(n8c_T2!=-1)]
  n8r_T2=n8r_T2[np.where(n8r_T2!=-1)]

  # Trasformare gli indici r e c dei vicini trovati sopra in indici lineari (np.ravel_multi_index)
  n8 = np.ravel_multi_index([n8r_T2, n8c_T2], I_mask.shape)

  # Eliminare il pixel appena analizzato dal vettore ToProcess e concatenare in coda al vettore
  # ToProcess i vicini che soddisfano le condizioni
  ToProcess = np.delete(ToProcess, -1)   
  ToProcess = np.append(ToProcess, n8)

  # Rimuovere eventuali pixel doppioni nel vettore ToProcess (np.unique)
  ToProcess = np.unique(ToProcess)

# Creare l'immagine con la segmentazione finale dei vasi in bianco sull'immagine originale
I_seg_originale = I_gray + K2
I_seg_mask = I_mask + K2

# Visualizzare l'immagine ottenuta
fig = px.imshow(I_seg_originale,color_continuous_scale='gray')
fig.show()

fig = px.imshow(I_seg_mask,color_continuous_scale='gray')
fig.show()