# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 17:30:00 2022

@author: lucia_jxuheg8
"""
# [3723.2475, 'N', 12158.3416, 'W', 1.0]
import json
from geopy import distance
import requests

class location():
    def __init__(self, urlCatalog, petID):
 
        self.pet1 = json.loads(requests.get("http://"+urlCatalog+"/searchPetbyID?pet_id="+str(petID)+"&idx=True").text)
        houseID=self.pet1["houseID"]
        self.house=json.loads(requests.get("http://"+urlCatalog+"/searchHousebyID?house_id="+str(houseID)).text)
        
        self.pet=self.pet1["pet"]
        self.activateServices=self.pet["Activateservices"]
        self.userID=self.house["userID"]
        self.devices = self.pet["devicesList"] 
               
        # print(self.devices[0])

    def control_position(self, message):
        if self.activateServices:
            topic = f"project/alert/{self.userID}/{self.pet['petName']}//location"
            name = self.pet["petName"]
            ranges = self.devices[0]["range"][-1]
            # For latitude, the northern direction (N) indicates positive number. 
            # The southern direction (S) indicates a negative value. 
            #For longitude, the eastern direction (E) indicates a positive number. 
            # And lastly, the western direction (W) is a negative number. 
            if ranges[1] == "S":
                ranges[0] = -1*ranges[0]
            if ranges[3] == "W":
                ranges[2] = -1* ranges[2]
            home = [ranges[0]/100, ranges[2]/100]
            radius = ranges[-1]
            
            # add random coordinates to the center of the house
            lat = home[0]+float(message["latitude"]) 
            long = home[1]+float(message["latitude"]) 
            dist = round(distance.distance(home, [lat,long]).km,3)
            
            if dist>radius:
                alert = f"WARNING: your pet {name}, has escaped. Distance from home: {dist}km"# ---------> alert telegram
                msg = {"measure" : dist,"alert" : alert}
                return (topic, msg)
            else:
                return
        else:
            return
                
             
             
if __name__ == "__main__":
    gps=location("192.168.43.2:8090",1)
                