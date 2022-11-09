# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:24:27 2022

@author: Santiago Caro
"""
# import client_thingspeak as thk
import client_mongoDB as mdb
import json
from datetime import datetime
# import time
# // Mass food (Sensor+Actuator)
# // Mass water (S+A)
# // Temperature rooms (S+A)

# // Temperature pet (S)
# // Hearth rate (S)
# // Respiration rate (S)
# // Location (S)

class Catalog:
    #Vecchio
    def __init__(self,filename): 
        self.filename = filename
        with open(self.filename) as f:
            self.file=json.load(f)
            
        self.avail_devices = ["collar", "termometer", "air_conditioning", "scale_food", "food_delivery", "scale_water", "water_delivery"] # they have to be lower case
        self.usersList = self.file["usersList"]
        self.houses = self.file["houses"]
        self.devices=[]
        # self.thingspeak = thk.client()
        self.mongo=mdb.client()
        
        # Variabiles used to assing new IDs:
        self.lastHouseID = 0
        self.lastDeviceID = 0
        self.lastUserID = 0
        self.lastPetID = 0
        self.lastRoomID = 0
        
        self.analyze()
        
    def analyze(self):
        # Creation of a list of all devices (rooms+pets)
        
        for house in self.houses: #Search in every house
            self.devices.append({"houseID":house["houseID"],"devicesList":[]})
            for room in house["roomsList"]:
                self.devices[-1]["devicesList"].extend(room["devicesList"])
            for pet in house["petsList"]:
                self.devices[-1]["devicesList"].extend(pet["devicesList"])
                
        # Inizialization of the variabiles used to assing new IDs
        #Search the lastID of houses, pets, rooms and devices
        for house in self.devices:
            if house["houseID"]>self.lastHouseID: self.lastHouseID = house["houseID"]
            for device in house["devicesList"]:
                if device["deviceID"]>self.lastDeviceID:self.lastDeviceID = device["deviceID"]
        for user in self.usersList:
            if user["userID"]>self.lastUserID: self.lastUserID = user["userID"]
        for house in self.houses:
            for pet in house["petsList"]:
                if pet["petID"]>self.lastPetID: self.lastPetID = pet["petID"]
            for room in house["roomsList"]:
                if room["roomID"]>self.lastRoomID: self.lastRoomID = room["roomID"]
       
    
    # INSERT
    def insertUser(self,userName, password, chatID):
        newUser = {}
        self.lastUserID+=1
        newUser["userName"] = userName
        newUser["password"] = password
        newUser["userID"] = self.lastUserID
        # Generare telegram bot e chat ID qui
        newUser["chatID"] = int(chatID)
        newUser["houses"] = []
        # print(newUser)
        self.usersList.append(newUser)
        self.file["usersList"] = self.usersList
        self.updateCatalog()
        # return("The user has succesfully been inserted")
        return newUser
        
    def insertHouse(self,house_name,user_id):
        newHouse = {}
        user_id = int(user_id)
        #If the user doesn´t exist there is the possibility to add a new one


        indexUser = self.searchUserbyID(user_id,True, idx=True)


        if indexUser==-1:
            user_id=self.lastUserID
            string_to_print= "User non esiste"
            return "User non esiste"
        if indexUser != None:
            newHouse={}
            newHouse["userID"]=user_id
            self.lastHouseID+=1
            newHouse["houseName"]=house_name
            newHouse["houseID"]=self.lastHouseID
            newHouse["roomsList"] = []
            newHouse["petsList"] = []
            
            self.houses.append(newHouse)
            self.file["houses"]=self.houses
            
            self.usersList[indexUser]["houses"].append({"houseID":self.lastHouseID})
            self.file["usersList"]=self.usersList
            self.updateCatalog()
            
            string_to_print = " The house has succesfully been inserted"
            return self.usersList[indexUser]

    def insertRoom(self, user_id, house_id, roomName):
        user_id = int(user_id); house_id=int(house_id)
        housesUser = self.searchHousesbyUserID(user_id)
        house = self.searchHousebyID(house_id)
        if house in housesUser:
            # check if the house has already a room with this name
            existingNames = [name["roomName"] for name in house["roomsList"]]
            if roomName not in existingNames:
                newRoom = {}
                self.lastRoomID +=1
                newRoom["roomID"] = self.lastRoomID
                newRoom["roomName"] = roomName
                newRoom["devicesList"] = []
                # newRoom["channelID"] = self.thingspeak.POST(roomName, newRoom["roomID"])  
                # update the catalog
                ix = self.houses.index(house)
                self.houses[ix]["roomsList"].append(newRoom)
                self.file["houses"] = self.houses
                # create MongoDB database and get channel id
                self.mongo.insertDatabase(f"{roomName}{self.lastRoomID}")
                self.updateCatalog()
                string_to_print = f" The room {roomName} has succesfully been inserted"
                return self.houses[ix]
             
            else:
                string_to_print = f"️ {roomName} is already present in house {house['houseName']}. Please retry with a new name"
                return string_to_print 
        else:
            string_to_print = "️ Room not inserted. Check IDs and retry"
            return string_to_print 
        
      
    def insertPet(self, user_id, house_id, petName):
        user_id = int(user_id); house_id=int(house_id)
        housesUser = self.searchHousesbyUserID(user_id)
        house = self.searchHousebyID(house_id)
        if house in housesUser:
            # check if the house has already a pet with this name
            existingNames = [name["petName"] for name in house["petsList"]]
            if petName not in existingNames:
                newPet = {}
                self.lastPetID+=1
                newPet["petID"] = self.lastPetID
                newPet["petName"] = petName
                newPet["devicesList"]= []
                newPet["Activateservices"] = True
                # newPet["channelID"] = self.thingspeak.POST(petName, newPet["petID"])  
                # update the catalog
                ix = self.houses.index(house)
                self.houses[ix]["petsList"].append(newPet)
                self.file["houses"] = self.houses
                self.mongo.insertDatabase(f"{petName}{self.lastPetID}")
                self.updateCatalog()
                return self.houses[ix]
                string_to_print = f" The pet {petName} has succesfully been inserted"
            else:
                string_to_print = f"️ Pet not inserted. Pet {petName} is already present in this house"
                return string_to_print
        else:
            string_to_print ="️ Pet not inserted. Check the IDs and retry"
            return string_to_print
        
    def insertDevice(self, user_id, house_id, ID, devicetype, ranges): # insert petID if you want to insert a collar or roomID in other case
        user_id = int(user_id); house_id = int(house_id); ID = int(ID) # INSERIRE CONTROLLO SUI RANGE
        # if the device is a collar, ranges is given as a list of lists, each sublist 
        # contains two elements, except for location: low value and high value, and for the last element (location) center coordinate and radius [x, N/S y, W/E, r]
        # for example [[19.0, 27.0], [120, 160], [15, 30], [3723.2475, "N", 12158.3416, "W", 1]] ( for location see https://it.rs-online.com/web/p/moduli-gnss-e-gps/1793714?cm_mmc=IT-PLA-DS3A-_-google-_-PLA_IT_IT_Semiconduttori_Whoop-_-(IT:Whoop!)+Moduli+GNSS+e+GPS-_-1793714&matchtype=&pla-333680702070&gclid=CjwKCAjwsJ6TBhAIEiwAfl4TWEdLaGT05lxQCid4X_bGCJLPH8oGkxAH5XqcbHU0LaejEFagqTGNghoCawQQAvD_BwE&gclsrc=aw.ds)
        ranges = eval(ranges) if type(ranges) is str else ranges
        housesUser = self.searchHousesbyUserID(user_id)
        house = self.searchHousebyID(house_id)
        if house in housesUser:
            # If we want to insert a device for a pet
            if devicetype.lower() == self.avail_devices[0].lower(): # Device for PET (collar)
                pets = self.searchPetsbyHouseID(house_id)
                existingIDs = [pet["petID"] for pet in pets]
                if ID in existingIDs:
                    pet = self.searchPetbyID(ID)
                    if not pet["devicesList"]: # if the list is empty (only one collar for each pet is permitted)   
                        newDevice = self.createDevice(user_id, house_id, pet,devicetype, ranges)
                        pet["devicesList"].append(newDevice)
                        if devicetype == "collar":
                            self.mongo.insertCollection(f"{pet['petName']}{pet['petID']}","basal_temperature")
                            self.mongo.insertCollection(f"{pet['petName']}{pet['petID']}","heart_rate")
                            self.mongo.insertCollection(f"{pet['petName']}{pet['petID']}","respiration_rate")
                            self.mongo.insertCollection(f"{pet['petName']}{pet['petID']}","location")
                            # return "Device inserted"
                         
                        
                        
                    else:
                        string_to_print = "️ Device not inserted: this pet already has a Collar"
                        return string_to_print
                else:
                    string_to_print = f"️ Device not inserted: pet {ID} does not exist in house {house_id}. \nAdd a new pet or try with another ID"
                    return string_to_print
              
            # If we want to insert a device for a ROOM             
            elif devicetype.lower() in self.avail_devices[1:]: # Device for ROOM (Termometer, Air Conditionig, Scale Food, Food delivery, Scale water, water deliver
                rooms = self.searchRoomsbyHouseID(house_id)
                existingIDs = [room["roomID"] for room in rooms]
                if ID in existingIDs:
                    room = self.searchRoombyID(ID)                    
                    newDevice = self.createDevice(user_id, house_id,room, devicetype, ranges)
                    room["devicesList"].append(newDevice)
                    ndev = len(room["devicesList"]) # number of devices in the room
                    # put = self.thingspeak.PUT(newDevice["deviceName"], room["channelID"],ndev) 
                    if devicetype == "termometer":
                        self.mongo.insertCollection(f"{room['roomName']}{room['roomID']}","temperature")
                    elif devicetype == "scale_food":
                        self.mongo.insertCollection(f"{room['roomName']}{room['roomID']}","mass_food")
                    elif devicetype == "scale_water":
                        self.mongo.insertCollection(f"{room['roomName']}{room['roomID']}","mass_water")
                    elif devicetype == "food_delivery":
                        self.mongo.insertCollection(f"{room['roomName']}{room['roomID']}","food_delivery")
                    elif devicetype == "water_delivery":
                        self.mongo.insertCollection(f"{room['roomName']}{room['roomID']}","water_elivery")
                    elif devicetype == "air_conditioning":
                        self.mongo.insertCollection(f"{room['roomName']}{room['roomID']}","air_conditioning")
                        
                else:
                    string_to_print = f"️ Device not inserted: room {ID} does not exist in house {house_id}. \nAdd a new room or try with another ID"
                    return string_to_print
            else:
                string_to_print = f"️ Device not inserted: this device is not available. \nInsert one of the following: {self.avail_devices}"
                return string_to_print
                            
            if "newDevice" in locals():   # If a new device have succesfully been created  (is present in local variables)          
                for house in self.devices:
                    if house["houseID"] == house_id:
                        house["devicesList"].append(newDevice)
                                
                self.file["houses"] = self.houses
                self.updateCatalog()
                string_to_print = f" The device {newDevice['deviceName']} has succesfully been inserted"
                return (string_to_print)
            else:
                string_to_print = " Device not inserted. Check the HouseID and UserID"
                return string_to_print
            
    #We have to improve this functios to generate the MQTT topics
    def createDevice(self, user_id, house_id,element, devicetype, ranges):
        # if the device is a collar, ranges is given as a list of lists, each sublist 
        # contains two elements [low value, high value], except for location that contains center coordinates and radius in km [x, N/S y, W/E, r]
        # for example [[19.0, 27.0], [120, 160], [15, 30], [3723.2475, N, 12158.3416, W, 1.0]] ( for location see https://it.rs-online.com/web/p/moduli-gnss-e-gps/1793714?cm_mmc=IT-PLA-DS3A-_-google-_-PLA_IT_IT_Semiconduttori_Whoop-_-(IT:Whoop!)+Moduli+GNSS+e+GPS-_-1793714&matchtype=&pla-333680702070&gclid=CjwKCAjwsJ6TBhAIEiwAfl4TWEdLaGT05lxQCid4X_bGCJLPH8oGkxAH5XqcbHU0LaejEFagqTGNghoCawQQAvD_BwE&gclsrc=aw.ds)
        newDevice = {}
        self.lastDeviceID+=1 
        newDevice["deviceID"] = self.lastDeviceID
        
        if devicetype.lower() == "collar":
            newDevice["deviceName"] = "Collar"
            newDevice["deviceType"] = "sensor"

            newDevice["measureType"] = ["basal temperature", "heart rate","respiration rate","location"]
            newDevice["range"] = ranges # given as [[19.0, 27.0], [120, 160], [15, 30], [3723.2475, "N", 12158.3416, "W", 1]

            newDevice["availableServices"] = ["MQTT", "REST"]
            newDevice["servicesDetails"] = {"serviceType": "MQTT","serviceIP": "mqtt.eclipse.org",
            "topic": [
                f"project/publish/pet/{element['petName']}/{element['petID']}/basal_temperature",
                f"project/publish/pet/{element['petName']}/{element['petID']}/heart_rate",
                f"project/publish/pet/{element['petName']}/{element['petID']}/respiration_rate",
                f"project/publish/pet/{element['petName']}/{element['petID']}/location"]},
            {"serviceType": "REST","serviceIP": "192.1.1.1:8080"}
            # project/publish/room/bedroom/1/temperature
        
        if devicetype.lower() == "termometer":
            newDevice["deviceName"] = "Termometer"
            newDevice["deviceType"] = "sensor"
            newDevice["measureType"] = ["temperature"]
            newDevice["range"] = ranges # given as [19.0,27.0] # celsius
            newDevice["availableServices"] = ["MQTT", "REST"]
            newDevice["servicesDetails"] = {"serviceType": "MQTT","serviceIP": "mqtt.eclipse.org",
                "topic": [f"project/publish/pet/{element['roomName']}/{element['roomID']}/temperature"]}, {"serviceType": "REST","serviceIP": "192.1.1.1:8080"}
            
        if devicetype.lower() == "air_conditioning":
            newDevice["deviceName"] = "Air Conditioning"
            newDevice["deviceType"] = "actuator"
            newDevice["measureType"] = []
            newDevice["range"] = [] 
            newDevice["availableServices"] = ["MQTT", "REST"]
            newDevice["servicesDetails"] = {"serviceType": "MQTT","serviceIP": "mqtt.eclipse.org",
                "topic": [f"project/publish/pet/{element['roomName']}/{element['roomID']}/air_conditioning"]},{"serviceType": "REST","serviceIP": "192.1.1.1:8080"}

        if devicetype.lower() == "scale_food": # (biancia)
            newDevice["deviceName"] = "Scale food"
            newDevice["deviceType"] = "sensor"
            newDevice["measureType"] = ["mass food"]
            newDevice["range"] = ranges # given as [200.00, 250.00, 12.30] # grams, grams, hh.mm # specify the time to refill
            newDevice["availableServices"] = ["MQTT", "REST"]
            newDevice["servicesDetails"] = {"serviceType": "MQTT","serviceIP": "mqtt.eclipse.org",
                "topic": [f"project/publish/pet/{element['roomName']}/{element['roomID']}/mass_food"]},{"serviceType": "REST","serviceIP": "192.1.1.1:8080"}

        if devicetype.lower() == "food_delivery":
            newDevice["deviceName"] = "Food delivery"
            newDevice["deviceType"] = "actuator"
            newDevice["measureType"] = []
            newDevice["range"] = []
            newDevice["availableServices"] = ["MQTT", "REST"]
            newDevice["servicesDetails"] = {"serviceType": "MQTT","serviceIP": "mqtt.eclipse.org",
                "topic": ["MySmartShelter/1/deliveryf"]},{"serviceType": "REST","serviceIP": "192.1.1.1:8080"}

        
        if devicetype.lower() == "scale_water": #(biancia)
            newDevice["deviceName"] = "Scale water"
            newDevice["deviceType"] = "sensor"
            newDevice["measureType"] = ["mass water"]
            newDevice["range"] = ranges # given as [200.00, 250.00] # grams, grams (no time to refill, always refill)
            newDevice["availableServices"] = ["MQTT", "REST"]
            newDevice["servicesDetails"] = {"serviceType": "MQTT","serviceIP": "mqtt.eclipse.org",
                "topic": [f"project/publish/pet/{element['roomName']}/{element['roomID']}/mass_water"]},{"serviceType": "REST","serviceIP": "192.1.1.1:8080"}

        if devicetype.lower() == "water_delivery":
            newDevice["deviceName"] = "Water delivery"
            newDevice["deviceType"] = "actuator"
            newDevice["measureType"] = []
            newDevice["range"] = []
            newDevice["availableServices"] = ["MQTT", "REST"]
            newDevice["servicesDetails"] = {"serviceType": "MQTT","serviceIP": "mqtt.eclipse.org",
                "topic": ["MySmartShelter/1/deliveryw"]},{"serviceType": "REST","serviceIP": "192.1.1.1:8080"}

        t=datetime.today()                      
        newDevice["lastUpdate"] = t.strftime("%Y-%m-%d %H:%M:%S")
        return newDevice     
  
    
    # MODIFY
    def modify(self,tipo,IDs,data):
        types=["house", "pet", "room", "device"]
        funcID=["searchHousebyID(IDs)","searchPetbyID(IDs[2])","searchRoombyID(IDs[2])","searchDevicebyID(IDs[2])"]
        dataKeys=list(data.keys())
        
        if tipo=="user":
                indexUser=self.searchUserbyID(IDs)
                if indexUser!=None:
                    for key in dataKeys:
                        self.file["usersList"][indexUser][key]=data[key]
                    self.updateCatalog()
                    
        elif tipo in types:
            housesUser= self.searchHousesbyUserID(IDs[0])
            house=self.searchHousebyID(IDs[1])
            # indexUser=self.searchUserbyID(IDs[0])
            if house in housesUser:
                indexHouse=self.file["houses"].index(house)
                if tipo=="house":
                    for key in dataKeys:
                        self.file["houses"][indexHouse][key]=data[key]
                else:
                    indexT=types.index(tipo)
                    # print(indexT)
                    element=eval("self."+funcID[indexT])
                    indexH=self.file["houses"].index(house)
                    exist=False
                    
                    if (tipo=="pet" or tipo =="room"):
                        tip=list(tipo)
                        tip[0]=tip[0].upper()
                        tip="".join(tip)
                        elements=eval("self.search"+tip+"sbyHouseID(IDs[1])")
                        indexElement=elements.index(element)
                        
                        if element in self.file["houses"][indexH][tipo+"sList"]:
                            for key in dataKeys:
                                self.file["houses"][indexH][tipo+"sList"][indexElement][key]=data[key]
                            exist=True
                    else:
                       
                        for pet in range(len(self.file["houses"][indexH]["petsList"])):
                            if element in self.file["houses"][indexH]["petsList"][pet]["devicesList"]:
                                indexDev=self.file["houses"][indexH]["petsList"][pet]["devicesList"].index(element)
                                for key in dataKeys:
                                    self.file["houses"][indexH]["petsList"][pet]["devicesList"][indexDev][key]=data[key]
                                exist=True
                        for room in range(len(self.file["houses"][indexH]["roomsList"])):
                            if element in self.file["houses"][indexH]["roomsList"][room]["devicesList"]:
                                indexDev=self.file["houses"][indexH]["roomsList"][room]["devicesList"].index(element)
                               
                                for key in dataKeys:
                                    self.file["houses"][indexH]["roomsList"][pet]["devicesList"][indexDev][key]=data[key]
                                exist=True
                                    
                    if exist==False:
                        print("Element not deleted. Check the IDs and retry")
                            
                    
                self.updateCatalog()
            else:
                string_to_print = "Element not deleted. Check the IDs and retry"
                return string_to_print
        else:
            string_to_print = "Invalid element type"
            return string_to_print
                
    
    
    # DELETE
    
    def delete(self,tipo,IDs):
        """

        Parameters
        ----------
        tipo : string
            user, house, pet, room, device
        IDs : list
            user----> user_id
            house---> [user_id,house_id]
            room,pet,device---> [user_id,house_id, room_id/pet_id/device_id]

        """
        types=["house", "pet", "room", "device"]
        funcID=["searchHousebyID(IDs)","searchPetbyID(IDs[2])","searchRoombyID(IDs[2])","searchDevicebyID(IDs[2])"]
        IDs = eval(IDs) if type(IDs) is str else IDs
        exist=False

        if tipo=="user":
                indexUser=self.searchUserbyID(IDs, idx=True)
                if indexUser!=None:
                    
                    houses=self.searchHousesbyUserID(IDs)
                    for house in houses:
                        self.file["houses"].remove(house)
                    
                    self.file["usersList"].pop(indexUser)
                    self.updateCatalog()
                    exist=True


            
        elif tipo in types:
            housesUser= self.searchHousesbyUserID(IDs[0])
            house=self.searchHousebyID(IDs[1])
            indexUser=self.searchUserbyID(IDs[0], idx=True)
            if house in housesUser:
                if tipo=="house":
                    self.file["houses"].remove(house)
                    self.file["usersList"][indexUser]["houses"].remove({"houseID":IDs[1]})
                else:
                    indexT=types.index(tipo)
                    element=eval("self."+funcID[indexT])
                    indexH=self.file["houses"].index(house)
                    exist=False
                    if (tipo=="pet" or tipo =="room"):
                        if element in self.file["houses"][indexH][tipo+"sList"]:

                            self.file["houses"][indexH][tipo+"sList"].remove(element)
                            name=eval("element['"+tipo+"Name']")
                            self.mongo.deleteDatabase(f"{name}{IDs[2]}")
                            exist=True
                        
                     
                    else:
                        for pet in range(len(self.file["houses"][indexH]["petsList"])):
                            if element in self.file["houses"][indexH]["petsList"][pet]["devicesList"]:
                                self.file["houses"][indexH]["petsList"][pet]["devicesList"].remove(element)
                                exist=True
                                database=self.file["houses"][indexH]["petsList"][pet]["petName"]+str(self.file["houses"][indexH]["petsList"][pet]["petID"])
                                
                        for room in range(len(self.file["houses"][indexH]["roomsList"])):
                            if element in self.file["houses"][indexH]["roomsList"][room]["devicesList"]:
                                self.file["houses"][indexH]["roomsList"][room]["devicesList"].remove(element)  
                                exist=True
                                database=self.file["houses"][indexH]["roomsList"][room]["roomName"]+str(self.file["houses"][indexH]["roomsList"][room]["roomID"])
                        if exist:
                            measures=element["measureType"]
                            if measures!=[]:
                                for measure in measures:
                                    # print(database)
                                    self.mongo.deleteCollection(database,measure)
        #     else:
        #         string_to_print = "️ Element not deleted. Check the IDs and retry"
        #         return string_to_print
        # else:
        #     string_to_print = " ️ Invalid element type"
        #     return string_to_print
        
        if exist:
            self.updateCatalog()
            string_to_print = "Element deleted succesfully"
            return (string_to_print)
        string_to_print = "️ Element not deleted. Check and retry"
        return string_to_print

        
   
    def statistics(self,nameid,measureType,start = "0"):
        """
        Parameters
        ----------
        nameid : str
            is the roomName or petName with relative id.
        collection : str
            measureType of sensor .replace " " con "_".
        start : str
           start selecting data.

        Returns
        -------
        the mongoDB array
        """
        measureType = measureType.replace(" ","_")
        # return self.mongo.searchbyTime(nameid,measureType,[start,"now"])
        try: 
            a = self.mongo.searchbyTime("Cucina3","temperature",["0","now"])
        except:
            a = "No data found"
       
        return a

        
    def searchUserbyName_Psw(self,userName,password,idx=False,askNew=False,):
        exist = False
        for user in self.usersList:
            if userName.lower() == user["userName"].lower() and  password == user["password"]:
                exist = True
                indexUser=self.usersList.index(user)
                return indexUser if idx else user
        
        if (exist == False and askNew==True): 
            a = True
            while a:
                response = input(f"User {userName} does not exist. Do you want to insert a new one? (Y/N)")
                if response=="Y":
                    userName=input("Insert the new username: ")
                    self.insertUser(userName)
                    a = False
                    return -1
                elif response == "N":
                    a = False
                    return 
                else:
                    print("Insert a valid option Y or N")
        elif(exist==False and askNew==False):
            print(f"User {userName} does not exist")
            string_to_print = "Name or pasword wrong. \nRetry or register new user"
            return string_to_print
        
        
        
        
    def Exit(self):
        pass
    
    def searchUserbyID(self, user_id, askNew=False, idx=False):
        exist = False
        user_id = int(user_id)
        for user in self.usersList:
            if user_id == user["userID"]:
                exist = True
                indexUser=self.usersList.index(user)
                return indexUser if idx else user
        
        if (exist == False and askNew==True): 
            a = True
            while a:
                response = input(f"User {user_id} does not exist. Do you want to insert a new one? (Y/N)")
                if response=="Y":
                    userName=input("Insert the new username: ")
                    self.insertUser(userName)
                    a = False
                    return -1
                elif response == "N":
                    a = False
                    return 
                else:
                    print("Insert a valid option Y or N")
        elif(exist==False and askNew==False):
            print(f"User {user_id} does not exist")
            return f"User {user_id} does not exist"
    
    def searchDevicebyID(self, ID):
        exist = False
        for house in self.devices:
            for device in house["devicesList"]:
                if device["deviceID"]==ID:
                    # print(device)
                    return device
                    exist=True
        if exist == False:
            print("Device not found")
            return 
    def searchDevicebyHouseID(self, house_id):
        exist=False
        for house in self.devices:
            if house["houseID"]==house_id:
                exist=True
                return house["devicesList"]
        if exist == False: print("House doesn't exist")
    
    def searchHousesbyUserID(self, user_id):
        
        indexUser = self.searchUserbyID(user_id,idx=True)
        if indexUser != None:
            housesIDs = [house["houseID"] for house in self.usersList[indexUser]["houses"]]
            houses=[]
            for house in self.houses:
                if (house["houseID"]in housesIDs): houses.append(house)
            return houses
        else:
            return []
        
    def searchHousebyID(self,house_id):
        exist=False
        for house in self.houses:
            if house["houseID"]==house_id:
                exist=True
                return house
        if exist == False:
            print (f"House with ID {house_id} doesn´t exist")
            return
    
    def searchPetsbyHouseID(self,house_id):
        exist=False
        for house in self.houses:
            if house["houseID"]==house_id:
                exist=True
                return house["petsList"]
        if exist == False: print("House doesn't exist")
    def searchPetbyID(self,pet_id,idx=False):
        exist=False
        for house in self.houses:
            for pet in house["petsList"]:
                if pet["petID"]==pet_id:
                    exist=True
                    if idx==False:
                        return pet
                    else:
                        return {"pet":pet, "houseID":house["houseID"]}
        if exist == False:
            print(f"Pet with ID {pet_id} doesn't exist")
            return
    def update_Activateservices(self, pet_id):
        pet_id = int(pet_id)
        pet = self.searchPetbyID(pet_id) 
        pet["Activateservices"] = not pet["Activateservices"]
        self.updateCatalog()
        return f"Service is {'on' if pet['Activateservices'] else 'off'}"
    
    def searchRoomsbyHouseID(self,house_id):
        exist=False
        for house in self.houses:
            if house["houseID"]==house_id:
                exist=True
                return house["roomsList"]
        if exist == False: print("House doesn't exist")
        
    def searchRoombyID(self,room_id, idx=False):
        exist=False
        for house in self.houses:
            for room in house["roomsList"]:
                if room["roomID"]==room_id:
                    exist=True
                    if idx==False:
                        return room
                    else:
                        return {"room":room, "houseID":house["houseID"]}
                
        if exist == False:
            print(f"Room with ID {room_id} doesn't exist")
            return
         
    
    def updateCatalog(self):
        t=datetime.today()                      
        self.file["lastUpdate"] = t.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filename, "w") as f:
            json.dump(self.file, f, indent = 4)
        self.__init__(self.filename)
        
                
     
            
if __name__ == '__main__':
    cat=Catalog("catalogo.json")
    
        
        
        
        
    
    
    