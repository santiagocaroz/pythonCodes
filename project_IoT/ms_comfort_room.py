# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 09:36:58 2022

@author: lucia_jxuheg8
"""
import json
import random
from datetime import datetime

import time
# import catalog_manager as catalog
import requests

# Temperature sensor LM35: 0.5°C Ensured Accuracy (at 25°C), Rated for Full −55°C to 150°C Range, Low Self-Heating, 0.08°C in Still Air
# Mass sensor Weigh Module WMS6002C-LX: Maximum Capacity 6.200 g, Readability 0.01 g


class comfort():
    
    def __init__(self, urlCatalog, roomID):
        
        # import the catalog to check which services are available:
        
        self.room = json.loads(requests.get("http://"+urlCatalog+"/searchRoombyID?room_id="+str(roomID)+"&idx=True").text)
        houseID=self.room["houseID"]
        self.house=json.loads(requests.get("http://"+urlCatalog+"/searchHousebyID?house_id="+str(houseID)).text)
        self.room=self.room["room"]
        self.userID=self.house["userID"]
        # print(self.house)        
        self.device_names = []

        self.devices = self.room["devicesList"]
        pets=self.house["petsList"]
        
        activateServices=False
        for pet in pets:
            if pet["Activateservices"]==True:
                activateServices=True
                
        self.activateServices=activateServices
                
        for device in self.devices:
            self.device_names.append(device["deviceName"])
        # print(self.device_names)
        
    def temperature(self,message):
        if self.activateServices:
            
            ix = self.device_names.index("Termometer") 
            low_limit = self.devices[ix]["range"][0]  # Celsius <- this is the limit set by the user when he register the device in the catalog
            high_limit = self.devices[ix]["range"][1]   # Celsius
            # print(low_limit)
            # print(message)
            measure = float(message["temperature"])
            timestamp = message["time"]
    
            
            topic = f"project/alert/{self.userID}/{self.room['roomName']}/temperature"
        
            if measure < low_limit:
                # send alert here via telegram bot !!!
                
                if "Air Conditioning" in self.device_names:
                    # activate Air conditioning at low_level temperature ---------> actuator
                    # send notification to the telegram bot
                    
                    alert = f" The temperature in room {self.room['roomName']} is too low: {measure} Celsius.\nThe air conditioning has been set to {low_limit} Celsius at {timestamp}."
                    msg = {"measure" : measure, "actuator" : "true", "value" : low_limit, "alert" : alert}
                else:
                    alert = f"The temperature in room {self.room['roomName']} is too low: {measure} Celsius. Time:{timestamp}\n"
                    msg = {"measure" : measure, "actuator" : "false", "value" : None, "alert" : alert}
                    
                return(topic,msg)
            
            elif measure > high_limit:
                # send alert here via telegram bot !!!
                # print("Air Cnditioning" in self.device_names, self.device_names)
                if "Air Conditioning" in self.device_names:
                    # activate Air conditioning at high_level temperature ---------> actuator
                    # send notification to the telegram bot
                    
                    alert = f"The temperature in room {self.room['roomName']} is too high: {measure} Celsius.\nThe air conditioning has been set to {high_limit} Celsius"
                    msg = {"measure" : measure, "actuator" : "true", "value" : high_limit, "alert" : alert}
                else:
                    alert = f"The temperature in room {self.room['roomName']} is too high: {measure} Celsius\n"
                    msg = {"measure" : measure, "actuator" : "false", "value" : None, "alert" : alert}
                return(topic, msg)
            else:
                return
        else:
            return
                
    
    def mass(self, element, message):
        if self.activateServices:
            ix = self.device_names.index(f"Scale {element}")
            low_limit = self.devices[ix]["range"][0]    # grams  <- this is the limit set by the user when he register the device in the catalog
            high_limit = self.devices[ix]["range"][1]   # grams
            measure = message[f"mass_{element}"]
            current_time = message["time"]
            current_time = current_time.split(".")
            current_time = float(current_time[-3]+"."+current_time[-2])
            
            if element == "food":
                time_to_eat = float(self.devices[ix]["range"][2] ) # hh.mm
                topic = f"project/alert/{self.userID}/{self.room['roomName']}/mass_food" 
            elif element == "water":
                time_to_eat = []
                topic = f"project/alert/{self.userID}/{self.room['roomName']}/mass_water" 
                
            delta_t = 0.15
            
            if (element == "food" and measure < low_limit and current_time>time_to_eat-delta_t and current_time<time_to_eat+delta_t) or (element == "water" and measure < low_limit):
                 
                    
                    element=element.title()+" delivery"  
                    if element in self.device_names:
                        # activate actuator at low_level mass ---------> actuator
                        # send notification to the telegram bot
                        alert = f"The {element} in room {self.room['roomName']} is over the limit: {measure} gr\nThe {element} has been fulfilled to {high_limit} gr"
                        msg = {"measure" : measure, "actuator" : "true", "value" : high_limit, "alert" : alert}
                        
                    else:
                        alert = f"The {element} in room {self.room['roomName']} is over the limit: {measure} gr\n"
                        msg = {"measure" : measure, "actuator" : "false", "value" : None, "alert" : alert}
                    return(topic, msg)
            else:
                return
        else:
            return
                    
   
if __name__ == "__main__":
    comfort=comfort("192.168.43.2:8090",1)
   
      
        