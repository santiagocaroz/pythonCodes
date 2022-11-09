# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 12:50:50 2022

@author: lucia_jxuheg8
"""

# [120, 160] hr, [15, 30] rr

import numpy as np
# from numpy import genfromtxt
# import random
from spectrum import arma_estimate,arburg,arma2psd
import matplotlib.pyplot as plt
import json
import requests

class health():
    
    def __init__(self, urlCatalog, petID):
        
        # n = random.randint(1,3)  # genero un numero random per selezionare il file da leggere
        # filename = "data0{}.csv".format(n)
        # print(filename)
        # # import the data acquired
        # my_data = genfromtxt(filename, delimiter=',') # data is a RR signal (distance of R waves for each cycle in ms)
               
        self.pet1 = json.loads(requests.get("http://"+urlCatalog+"/searchPetbyID?pet_id="+str(petID)+"&idx=True").text)
        
        houseID=self.pet1["houseID"]
        self.house=json.loads(requests.get("http://"+urlCatalog+"/searchHousebyID?house_id="+str(houseID)).text)
        
        self.pet=self.pet1["pet"]
        self.activateServices=self.pet["Activateservices"]
        self.userID=self.house["userID"]
        self.devices = self.pet["devicesList"]            
        
        
    def heart_rate(self, message):
        if self.activateServices:
            # print("Si")
            topic = f"project/alert/{self.userID}/{self.pet['petName']}/heart_rate"
            my_data = message["signal"]
            heart_lim = self.devices[0]["range"][1]
            hr = int( 60/(np.mean(my_data)*10**(-3)) );  # bpm
            # print(f"hr = {hr} beat per minute")
            if hr < heart_lim[0] or hr > heart_lim[1]:
                alert = f"WARNING, the heart rate is out of range: {hr} bpm" # ---------> send alert via telegram bot
                msg = {"measure" : hr, "alert" : alert}
                return (topic, msg)
            else:
                return
        else:
            return
    
    def respiration_rate(self, message):
        if self.activateServices:
            topic = f"project/alert/{self.userID}/{self.pet['petName']}/respiration_rate"
            my_data = message["signal"]
            # current_time = message["time"]
            breath_lim = self.devices[0]["range"][2]
            e = []
            
            # compute the variance for orders between 1 and 50
            for n in range(0,49):
                b,a, var = arma_estimate(my_data, n+1, n+1, int(len(my_data)/2))
                e.append(var)
            # compute the asintotic variance as the last value+5% , this will be our threshold to choose the order  
            asint = e[-1]*1.05
            
            # choose the order as the lowest value correponding to the minimum variance above the threshold asint
            idx=[]
            [idx.append(i) for i in range(len(e)) if e[i] < asint]
            order = idx[0]
            
            # Estimate the complex autoregressive parameters by the Burg algorithm.
            AR, P, k = arburg(my_data-np.mean(my_data), order)
            # Computes power spectral density given ARMA values
            PSD = arma2psd(AR,sides='centerdc' )
            # eliminate spectral replication (negative values)
            PSD = PSD[int(len(PSD)/2-1):-1] 
            # frequency axis
            f = np.linspace(0.0,3.14, int(len(PSD)))/(2*3.14)/(np.mean(my_data)*10**-3)
            # identify the band in which I expect the peak for Respiration rate  (HF)
            inf = np.where(f>0.2)
            inf = inf[0][0]        
            sup = np.where(f<0.5)
            sup = sup[0][-1]
            # find the maximum in the HF band, corresponding to the breath rate per second
            maximum = np.where(PSD[inf:sup] == np.amax(PSD[inf:sup]))
            maximum = maximum[0]+inf
            # convert the breath rate in breath per minute
            rr = int(f[maximum]*60)
            # print(f"rr = {rr} breath per minute")
            
            # uncomment the following line to visualize the PSD
            # self.plot_PSD(f, PSD, maximum)
            
            
            if rr< breath_lim[0] or rr> breath_lim[1]:
                alert = f"WARNING, the respiration rate is out of range: {rr} breaths per minute"  # ---------> send alert via telegram bot
                msg = {"measure" : rr, "alert" : alert}
                return (topic, msg)
            else:
                return 
        else:
            return
        
    def plot_PSD(self, f,PSD, maximum):
        plt.plot(f, PSD/np.max(PSD))
        plt.plot(f[maximum], PSD[maximum]/np.max(PSD), "x")
        plt.title('PSD')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Normalised PSD')
        
        plt.show()
        
    def basal_temperature(self, message):
        if self.activateServices:
            
            topic = f"project/alert/{self.userID}/{self.pet['petName']}/basal_temperature"
            temp_limit = self.devices[0]["range"][0]   
            low_limit = temp_limit[0]       # Celsius <- this is the limit set by the user when he register the device in the catalog
            high_limit = temp_limit[1]      # Celsius
            
            measure = float(message["basal_temperature"])
            timestamp = message["time"]
            # print(measure)
            # topic = f"project/alert/room/{self.room['roomName']}/{self.room['roomID']}/temperature"
            if measure < low_limit:
                # send alert here via telegram bot !!!
                alert = f"The basal temperature of {self.pet['petName']} is too low: {measure} Celsius. Time:{timestamp}\n"
                msg = {"measure" : measure, "alert" : alert}
                
                return(topic,msg)
            
            elif measure > high_limit:
                # send alert here via telegram bot !!!
                alert = f"The basal temperature of {self.pet['petName']} is too high: {measure} Celsius. Time:{timestamp}\n"
                msg = {"measure" : measure, "alert" : alert}
                return(topic, msg)
            else:
                return
        else:
            return
   
    
if __name__ == '__main__':

    puppyt=health("192.168.43.2:8090",1)    
