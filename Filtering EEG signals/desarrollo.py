# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 14:13:50 2019

@author: santo
"""
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import scipy.signal as signal
import matplotlib.pyplot as plt
import pandas as pd

def fkernel(m, f, w):
    m = np.arange(-m/2, (m/2)+1)
    b = np.zeros((m.shape[0]))
    b[m==0] = 2*np.pi*f # No division by zero
    b[m!=0] = np.sin(2*np.pi*f*m[m!=0]) / m[m!=0] # Sinc
    b = b * w # Windowing
    b = b / np.sum(b) # Normalization to unity gain at DC
    return b

def firws(m, f , w , t = None):
    """
    Designs windowed sinc type I linear phase FIR filter.
    Parameters:        
        m: filter order.
        f: cutoff frequency/ies (-6 dB;pi rad / sample).
        w: vector of length m + 1 defining window. 
        t: 'high' for highpass, 'stop' for bandstop filter. {default low-/bandpass}
    Returns:
        b: numpy.ndarray
            filter coefficients 
    """
    f = np.squeeze(f)
    f = f / 2; 
    w = np.squeeze(w)
    if (f.ndim == 0): #low pass
        b = fkernel(m, f, w)
    else:
        b = fkernel(m, f[0], w) #band
    
    if (f.ndim == 0) and (t == 'high'):
        b = fspecinv(b)
    elif (f.size == 2):
        b = b + fspecinv(fkernel(m, f[1], w)) #reject
        if t == None or (t != 'stop'):
            b = fspecinv(b) #bandpass        
    return b

## Spectral inversion
def fspecinv(b):
    b = -b
    b[int((b.shape[0]-1)/2)] = b[int((b.shape[0]-1)/2)]+1
    return b

def filter_design(srate, locutoff = 0, hicutoff = 0, revfilt = 0):
    #Constants
    TRANSWIDTHRATIO = 0.25;
    fNyquist = srate/2;  
    
    #The prototipical filter is the low-pass, we design a low pass and transform it
    if hicutoff == 0: #Convert highpass to inverted lowpass
        hicutoff = locutoff
        locutoff = 0
        revfilt = 1 #invert the logic for low-pass to high-pass and for
                    #band-pass to notch
    if locutoff > 0 and hicutoff > 0:
        edgeArray = np.array([locutoff , hicutoff])
    else:
        edgeArray = np.array([hicutoff]);
    
    #Not negative frequencies and not frequencies above Nyquist
    if np.any(edgeArray<0) or np.any(edgeArray >= fNyquist):
        print('Cutoff frequency out of range')
        return False  
    
    # Max stop-band width
    maxBWArray = edgeArray.copy() # Band-/highpass
    if revfilt == 0: # Band-/lowpass
        maxBWArray[-1] = fNyquist - edgeArray[-1];
    elif len(edgeArray) == 2: # Bandstop
        maxBWArray = np.diff(edgeArray) / 2;
    maxDf = np.min(maxBWArray);
    
    # Default filter order heuristic
    if revfilt == 1: # Highpass and bandstop
        df = np.min([np.max([maxDf * TRANSWIDTHRATIO, 2]) , maxDf]);
    else: # Lowpass and bandpass
        df = np.min([np.max([edgeArray[0] * TRANSWIDTHRATIO, 2]) , maxDf]);
    
    print(df)
    
    filtorder = 3.3 / (df / srate); # Hamming window
    filtorder = np.ceil(filtorder / 2) * 2; # Filter order must be even.
    
    # Passband edge to cutoff (transition band center; -6 dB)
    dfArray = [[df, [-df, df]] , [-df, [df, -df]]];
    cutoffArray = edgeArray + np.array(dfArray[revfilt][len(edgeArray) - 1]) / 2;
    print('pop_eegfiltnew() - cutoff frequency(ies) (-6 dB): '+str(cutoffArray)+' Hz\n');
    # Window
    winArray = signal.hamming(int(filtorder) + 1);
    # Filter coefficients
    if revfilt == 1:
        filterTypeArray = ['high', 'stop'];
        b = firws(filtorder, cutoffArray / fNyquist, winArray, filterTypeArray[len(edgeArray) - 1]);
    else:
        b = firws(filtorder, cutoffArray / fNyquist, winArray);

    return filtorder, b;
def matrices_archivos(file,n):
    EEG_C= np.loadtxt(file, delimiter=',',skiprows=6, usecols=(n))
    return EEG_C
def umbral(senal,epoca,fs=250,umb=45):
    mod=len(senal)%(epoca*fs)
    N=(len(senal)-mod)/(epoca*fs)
    signalSplit=np.split(senal[:len(senal)-mod],N)
    r=senal[len(senal)-mod:]
    signalSplit=signalSplit+[r]
    
#    for segmento in range(10):
#        time=np.arange(0, len(signalSplit[segmento])/fs,1/fs)
#        plt.plot(time,signalSplit[segmento])
#        plt.show()
    
    for segmento in signalSplit:
        if np.max(segmento)>umb or np.min(segmento)<-umb:
            for j in range(len(segmento)):
                segmento[j]=0
    signalComplete=np.concatenate(signalSplit)
      
    return signalComplete

def analisis(senal,fs=250):
  
  tiempo=np.arange(0, len(senal)/fs,1/fs)
  plt.plot(tiempo,senal)
  #plt.plot(tiempo,senal)
  plt.show()
  f,pot=signal.welch(senal,fs,'hanning',fs*2,fs)
  plt.plot(f,pot)
  plt.show()
  return f,pot

def filtros(senal,fs=250):
  order, lowpass = filter_design(fs, locutoff = 0, hicutoff = 49, revfilt = 0);
  order, highpass = filter_design(fs, locutoff = 0.5, hicutoff = 0, revfilt = 1);

  senal_filtrada_pasaaltas = signal.filtfilt(highpass, 1, senal);
  senal_filtrada_pasabajas = signal.filtfilt(lowpass, 1, senal_filtrada_pasaaltas);
  EEGfiltrada=umbral(senal_filtrada_pasabajas,1)
  #plt.plot(tiempo,EEGfiltrada)
  #plt.show()
  return EEGfiltrada

EEG2=matrices_archivos("P1_RAWEEG_2018-11-15_OjosCerrados_2min.txt",2)
EEG3=matrices_archivos("P1_RAWEEG_2018-11-15_OjosCerrados_2min.txt",3)
EEG4=matrices_archivos("P1_RAWEEG_2018-11-15_OjosCerrados_2min.txt",4)
fs=250
#analisis(EEG2)

EEGfiltrada2=filtros(EEG2)
EEGfiltrada3=filtros(EEG3)
#analisis(EEGfiltrada2)
#analisis(EEGfiltrada3)

senalbipolar32=EEGfiltrada3-EEGfiltrada2

f,pot=analisis(senalbipolar32)  
  



