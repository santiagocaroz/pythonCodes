# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 12:50:50 2022

@author: Giorgio Chiesa
"""

# [120, 160] hr, [15, 30] rr
import os
import numpy as np
# from numpy import genfromtxt
# import random
import matplotlib.pyplot as plt
import json
import pandas as pd
import seaborn as sns
import requests

class stats():
    
    def __init__(self, urlCatalog):
        
        # n = random.randint(1,3)  # genero un numero random per selezionare il file da leggere
        # filename = "data0{}.csv".format(n)
        # print(filename)
        # # import the data acquired
        # my_data = genfromtxt(filename, delimiter=',') # data is a RR signal (distance of R waves for each cycle in ms)
               
        self.urlCatalog = urlCatalog          
        
        self.avail_measure = {"temperature": {"ytick": "Temperature (°C)"},
                              "mass food": {"ytick": "Mass (kg)"},
                              "basal temperature": {"ytick": "Temperature (°C)"},
                              "heart rate": {"ytick": "Rate (bpm)"},
                              "respiration rate": {"ytick": "Rate (bpm)"},
                              "location": {"ytick": "Temperature (°C)"},
                              }

        
    def stats_for(self, servizio):
        print(self.urlCatalog+"/statistics", servizio)
        x = json.loads(requests.post(self.urlCatalog+"/statistics", data=servizio).text)
        link_img = f"img/{servizio['userID']}_{servizio['measureType']}.jpg"
        link_xls = f"img/{servizio['userID']}_{servizio['measureType']}.xlsx"
        topic = f"project/alert/{servizio['userID']}"
        if type(x) is not str and x["documents"]:
            plt.close("all")
            df = pd.DataFrame(x["documents"])
            df = df.sort_values("time")
            time = []
            for t in df.time:
                Y,M,D,h,m,s =  t.split(".")
                time.append(pd.Timestamp( year=int(Y), month=int(M), day=int(D), hour=int(h), minute=int(m), second=int(s)))
            df.time = time
            y_name = [c for c in df.columns if c not in ["_id","time"]][0]
            g = sns.relplot(x="time", y=y_name, data=df,  hue=y_name, palette="coolwarm")
            
            g.set_xlabels("Timepoint"); g.set_ylabels(self.avail_measure[y_name]["ytick"])
            g.fig.suptitle(y_name.capitalize() )
            # ax.xaxis.set_major_formatter(dates.DateFormatter("%d-%b"))
    
            t = pd.date_range(start=min(df.time),
                              end= max(df.time),
                              periods=7)
            # ax.set_xticks(t.strftime('%Y-%m-%d %X').values)
            g.set_xticklabels(rotation=30)
            g.tight_layout()
            if not os.path.isdir("img"):
                os.mkdir("img")
            g.savefig(link_img)
            df.to_excel(link_xls)
        
            # send alert here via telegram bot !!!
            max_ = np.round(np.max(df[y_name].values),1); min_ =  np.round(np.min(df[y_name].values),1);
            average = np.round(np.mean(df[y_name].values),2)
            # num_out = np.where
            alert = f"Some statistics:\nMax: {max_}\nMin: {min_}\nAverage: {average}"
            msg = {"alert" : alert, "img": link_img, "file": link_xls}
            return(topic, msg)
        else:
            return(topic, {"alert" : "No data sensor found"})

   
    
if __name__ == '__main__':

    puppyt=stats("192.168.43.2:8090")    
