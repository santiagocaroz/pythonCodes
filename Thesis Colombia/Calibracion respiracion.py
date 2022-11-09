# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 00:28:32 2022

@author: Santiago Caro
"""

import analisis_datos as anl
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
profe=anl.analisisXpersona("profe1SCZ.txt","PULSO")
profe1=anl.analisisTotal([profe],"no")

ADC=[i-profe.Filt_RESP[1][300] for i in profe.Filt_RESP[1][300:]]
time=[i-profe.Filt_RESP[0][300] for i in profe.Filt_RESP[0][300:]]


media=sum(ADC)/len(ADC)
ADC=[adc-media for adc in ADC]

maximo=max(max(ADC),abs(min(ADC)))

ADC=[adc/maximo for adc in ADC]




df = pd.read_excel('RESPIRACION ORIENTE.xlsx', sheet_name='Recording0002R17')

flow=[]
timeFlow=[]
BPM=[]

BPM=[df["BPM  "][i] for i in range(len(df["BPM  "]))]
    
    
for i in range(len(df["Flow lmin"])):
    # flow.append(df["Flow lmin"][i]*30+400)
    flow.append(df["Flow lmin"][i])
    timeFlow.append(i*1000)


offset=sum(flow)/len(flow)

flow=[i-offset for i in flow]



maxim=max([max(flow),abs(min(flow))])

for i in range(len(flow)):
    flow[i]=flow[i]/maxim
    
    
freq=profe1.freqxtramos(ADC,time,0,len(ADC),1,"RESP")
freq2=profe1.freqxtramos(flow,timeFlow,0,len(flow),1,"RESP")

time=[i/1000 for i in time]
timeFlow=[i/1000 for i in timeFlow]
plt.plot(time,ADC)
plt.plot(timeFlow,flow)
plt.legend(["Sensor de respiración","FLUKE VT650"], fontsize=20)   
plt.axhline(freq[1])
plt.axhline(freq2[1]) 
plt.xlabel("Tiempo(s)", fontsize=20)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.xlim(0,200)

plt.figure()

freq[2]=[i/1000 for i in freq[2]]
freq2[2]=[i/1000 for i in freq2[2]]

plt.step(freq[2],freq[0])
plt.step(freq2[2],freq2[0])
# plt.plot(freq[2][25],freq[0][25],".",markersize=15)
# plt.plot(freq2[2][25],freq2[0][25],".",markersize=15)
plt.xlabel("Tiempo(s)", fontsize=20)
plt.ylabel("Frecuencia respiratoria (BPM)", fontsize=20)
plt.legend(["Sensor de respiración","FLUKE VT650"], fontsize=20)   
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.xlim(0,200)
# plt.plot(timeFlow,BPM)

error =[abs(freq[0][i]-freq2[0][i]) for i in range(len(freq[0]))]
error=error[0:-1]
promErr=sum(error)/len(error)