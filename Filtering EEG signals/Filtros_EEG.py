# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 08:47:39 2019

@author: Alejandro
"""

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
#%%
def mfreqz(b,a,order,nyq_rate = 1):
    
    """
    Plot the impulse response of the filter in the frequency domain

    Parameters:
        
        b: numerator values of the transfer function (coefficients of the filter)
        a: denominator values of the transfer function (coefficients of the filter)
        
        order: order of the filter 
                
        nyq_rate = nyquist frequency
    """
    
    w,h = signal.freqz(b,a);
    h_dB = 20 * np.log10 (abs(h));
    
    plt.figure();
    plt.subplot(311);
    plt.plot((w/max(w))*nyq_rate,abs(h));
    plt.ylabel('Magnitude');
    plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)');
    plt.title(r'Frequency response. Order: ' + str(order));
    [xmin, xmax, ymin, ymax] = plt.axis();
    plt.grid(True);
    
    plt.subplot(312);
    plt.plot((w/max(w))*nyq_rate,h_dB);
    plt.ylabel('Magnitude (db)');
    plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)');
    plt.title(r'Frequency response. Order: ' + str(order));
    plt.grid(True)
    plt.grid(True)
    
    
    plt.subplot(313);
    h_Phase = np.unwrap(np.arctan2(np.imag(h),np.real(h)));
    plt.plot((w/max(w))*nyq_rate,h_Phase);
    plt.ylabel('Phase (radians)');
    plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)');
    plt.title(r'Phase response. Order: ' + str(order));
    plt.subplots_adjust(hspace=0.5);
    plt.grid(True)
    plt.show()

#%%
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

fs = 250;
##design
order, lowpass = filter_design(fs, locutoff = 0, hicutoff = 50, revfilt = 0);
##plot
#mfreqz(lowpass,1,order, fs/2);
#
order, highpass = filter_design(fs, locutoff = 5, hicutoff = 0, revfilt = 1);
##plot
#mfreqz(highpass,1,order, fs/2);




def matrices_archivos(file,n):
    data = open(file, 'r')
    fila=data.readlines()
    EEG_C=np.zeros(len(fila))
    for i in np.arange(6,len(fila)):
        dato=fila[i].find(' ')
        for j in (np.arange(n)):
            dato1=fila[i].find(' ',dato+j)
            dato2=fila[i].find(',',dato1)
            dato=dato1
        EEG_C[i]=float(fila[i][dato1:dato2])
    EEG_C=EEG_C[6:len(EEG_C)]
    return EEG_C


EEG_C=matrices_archivos("P1_RAWEEG_2018-11-15_Electrobisturí1_3min.txt",2)
#plt.plot(EEG_C)
#plt.show()
fs=250
tiempo=np.arange(0, len(EEG_C)/250,1/250)

senal_filtrada_pasaaltas = signal.filtfilt(highpass, 1, EEG_C);
senal_filtrada_pasabajas = signal.filtfilt(lowpass, 1, senal_filtrada_pasaaltas);
#senal_filtrada_pasabajas = signal.filtfilt(notch, 1, senal_filtrada_pasabajas);
#senal_filtrada=np.fft.fft(senal_filtrada_pasabajas)
#plt.plot(tiempo,senal_filtrada_pasabajas)
f,pot=signal.welch(senal_filtrada_pasabajas,fs,'hanning',fs*2,fs)
#plt.plot(f,pot)
#plt.xlim(0,10)
#plt.plot(tiempo[0:10*fs],senal_filtrada_pasabajas[0:10*fs])
#plt.show()



def umbral(signal,epoca,fs=250,umb=45):
    mod=len(signal)%(epoca*fs)
    N=(len(signal)-mod)/(epoca*fs)
    signalSplit=np.split(signal[:len(signal)-mod],N)
    r=signal[len(signal)-mod:]
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
      
    return signalSplit


EEGconUmbral=umbral(senal_filtrada_pasabajas ,2)

#
#plt.subplot(2,2,1)
#plt.plot(tiempo, EEG_C)
#plt.subplot(2,2,2)
#plt.plot(tiempo,senal_filtrada_pasaaltas)
#plt.subplot(2,2,3)
#plt.plot(tiempo,senal_filtrada_pasabajas)
#plt.subplot(2,2,4)
#plt.plot(tiempo,EEGconUmbral)
#plt.show()



