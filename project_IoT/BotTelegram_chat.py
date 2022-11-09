import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from telepot.namedtuple import KeyboardButton
# from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
# from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent

import json
import requests
from termcolor import colored
import hashlib
from pandas.tseries.offsets import DateOffset
from telepot.delegate import pave_event_space, per_chat_id, create_open, include_callback_query_chat_id
import paho.mqtt.client as pahoMqtt

import pandas as pd

import socket

class InsertBot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(InsertBot, self).__init__(*args, **kwargs)
        self._count = 0
        self.action = ""
        self.params= {}
        self.topics=[]
        self._paho = None
        self.broker= "mqtt.eclipseprojects.io"
        self.port = 1883
        self.to_know = []
        self.server_url ="http://"+ socket.gethostbyname(socket.gethostname())+":8090"
        print(self.server_url)
        self.user ={}
        self.final_message=""
        self.houses =[]
        
        self.avail_devices = {"collar":{"description":"Collar has different sensors, you should set the range for all of them:\n -termometer (min, max temperature)\n -Heart rate (min,max avaible range)\n -Respiration rate (min,max avaible range)\n -Location (position, radius) \n",
                                      "to_know":["minimum temperature","maximum temperature","minimum heart rate","maximum heart rate","minimum respiration rate","maximum respiration rate","position","radius (km)"],
                                      "struct":"[[float(params['minimum temperature']),float(params['maximum temperature'])],[float(params['minimum heart rate']),float(params['maximum heart rate'])],[float(params['minimum respiration rate']),float(params['maximum respiration rate'])],[float(params['latitude']),'N',float(params['longitude']),'W',float(params['radius (km)'])]]"
                                      }, 
                              "termometer":{"description":"You can set a range over there send an alert to actuators \nYou should set the min temperature:",
                                            "to_know":["min","max"],
                                            "struct":"[float(params['min']),float(params['max'])]"
                                            },
                              "air_conditioning":{"description":"This actuator will switch on the air conditioning",
                                                  "struct":"[]"
                                                  }, 
                              "scale_food":{"description":"You can choose a range to generate an alert \nYou should set:\n- the minimum mass to refill the food delivery, \n- tha maximum mass of food delivery, \n- the time to execute the check (hh.mm)",
                                            "to_know":["minimum","maximum","time"],
                                            "struct":"[float(params['minimum']),float(params['maximum']),float(params['time'])]"
                                            }, 
                              "food_delivery":{"description":"This actuator will refill the food",
                                                "struct":"[]"
                                                },
                              "scale_water":{"description":"You can choose a range to generate an alert \nYou should set:\n- the minimum mass of water to refill the water delivery, \n- tha maximum mass of water delivery, \nalways refill water",
                                            "to_know":["minimum","maximum"],
                                            "struct":"[float(params['minimum']),float(params['maximum'])]"
                                            },  
                              "water_delivery":{"description":"This actuator will refill the water",
                                                "struct":"[]"
                                                }
                              } # they have to be lower case

        self.avail_measure = {"temperature": {"ytick": "Temperature (°C)"},
                              "mass food": {"ytick": "Mass (kg)"},
                              "basal temperature": {"ytick": "Temperature (°C)"},
                              "heart rate": {"ytick": "Rate (bpm)"},
                              "respiration rate": {"ytick": "Rate (bpm)"},
                              "location": {"ytick": "Temperature (°C)"},
                              }
        
        
        
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        if content_type == "text":
            message = msg["text"]
            print("msg",colored(" ".join((content_type,chat_type,message)) , "red"))
            
            if message == "/insert":
                if not "userID" in self.user:
                    self.bot.sendMessage(chat_ID, text="Register or login first :)")
                    return
                buttons = [[InlineKeyboardButton(text='House', callback_data="insertHouse"),
                            InlineKeyboardButton(text='Room', callback_data="insertRoom"),
                            InlineKeyboardButton(text='Pet', callback_data="insertPet"),
                            InlineKeyboardButton(text='Device', callback_data="insertDevice")]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text="What do you want to insert ?", reply_markup=keyboard)
            elif message == "/profile":
                # print(str(self.user) + str(self.houses))
                if "userName" in self.user:
                    strUser = f"""👤 {self.user['userName']}\n"""
                    if self.user["houses"] != []:
                        strUser += "\n -------- \n".join([f"""🏡 House: {h['houseName']} \nRooms: \n""" + "\n".join([f""" ⛺️ {r['roomName']} \nDevices: \n""" + "\n".join([f""" {s['deviceName']} """ + (str(s['range']) if len(s['range'])>0 else "") for s in r["devicesList"]]) for r in h["roomsList"]]) + str("\nPets: \n" +"\n".join([f"🐶 {p['petName']} "+("➰" if len(p['devicesList'])>0 else "" ) for p in h["petsList"]]) if "petsList" in h else "") for n,h in enumerate(self.houses)])
                    self.bot.sendMessage(chat_ID, text=strUser)
                else:
                    self.bot.sendMessage(chat_ID, text="Register or login first :)")
                    # self.bot.sendMessage(chat_ID, text=json.dumps(self.houses, indent=4))
            elif message == "/register":
                self.action = self.send_request
                self.params={"uri":"insertUser" ,"userName":"","password":"","chatID":chat_ID}
                self.to_know=["userName","password"]
                print(colored(f"{self.action}\n{self.params}\n{self.to_know}\nUser:{self.user}", "green"))
                #reply = ForceReply()
                self.bot.sendMessage(chat_ID, text="Insert name and password:\nName")
            elif message == "/login":
                self.action = self.send_request
                self.params={"uri":"searchUserbyName_Psw","userName":"","password":"","chatID":chat_ID}
                self.to_know=["userName","password"]
                print(colored(f"{self.action}\n{self.params}\n{self.to_know}\nUser:{self.user}", "green"))
                #reply = ForceReply()
                self.bot.sendMessage(chat_ID, text="Insert your name")
            elif message == "/delete":
                buttons = [[InlineKeyboardButton(text='User', callback_data="delete_User"),
                            InlineKeyboardButton(text='House', callback_data="delete_House"),
                            InlineKeyboardButton(text='Room', callback_data="delete_Room"),
                            InlineKeyboardButton(text='Pet', callback_data="delete_Pet"),
                            InlineKeyboardButton(text='Device', callback_data="delete_Device")]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text="What do you wanna delete ?", reply_markup=keyboard)
            elif message == "/exit":
                self.action = None
                self.params={}
                self.to_know = []
                self.bot.sendMessage(chat_ID, text="Azione annullata")
            elif message == "/services":
                self.params={"uri":"update_Activateservices" ,"pet_id":""}
                my_dev = []
                for h in self.houses:
                    for p in h["petsList"]:
                        my_dev.append({"name" :f"{'🟢' if p['Activateservices'] else '🔴'}  {p['petName']}",
                                       "name_id": f"{p['petID']}"})
                if my_dev:
                    buttons = [[InlineKeyboardButton(text=f'{obj["name"]}', callback_data=f"servToggle_{obj['name_id']}")]
                                           for obj in my_dev ]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text="Switch ON/OFF services for", reply_markup=keyboard)  
                else:
                    self.bot.sendMessage(chat_ID, text="Register a pet first")  
                    self._exit()
            elif message == "/statistics":
                self.params={"nameid":"","measureType":None,"start":0}
                my_dev = []
                for h in self.houses:
                    for r in h["roomsList"]:
                        for d in r["devicesList"]:
                            if d["measureType"]:
                                for measure in d["measureType"] : 
                                    my_dev.append({f"{r['roomName']}{r['roomID']}": {"name":f"{d['deviceName']} in {r['roomName']}",
                                                                                     "measureType": measure }})
                for h in self.houses:
                    for r in h["petsList"]:
                        for d in r["devicesList"]:
                            if d["measureType"]:
                                for measure in d["measureType"] : 
                                    my_dev.append({f"{r['petName']}{r['petID']}":  {"name":f"{d['deviceName']} for {r['petName']}",
                                                                                      "measureType": measure }})
                if my_dev:
                    buttons =[]
                    for obj in my_dev:
                        buttons += [[InlineKeyboardButton(text=f'{ob["name"]} - {ob["measureType"]}', callback_data=f"statistics_{nameidx}_{ob['measureType']}")]
                                       for nameidx,ob in obj.items() ]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text="What do you want the stats for?", reply_markup=keyboard)  
                else:
                    self.bot.sendMessage(chat_ID, text="No sensor for statistics", reply_markup=keyboard)  
                    self._exit(chat_ID)

            elif self.to_know:
                if self.to_know[0] == "password":
                	self.bot.deleteMessage(telepot.message_identifier(msg))
                self.params.update({self.to_know[0]: message})
                self.to_know.pop(0)
                if self.to_know:
                    if self.to_know[0] == "position":
                        markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Location', request_location=True)]]) 
                        self.bot.sendMessage(chat_ID, text=self.to_know[0], reply_markup=markup)

                    else:
                        self.bot.sendMessage(chat_ID, text=self.to_know[0])
                else:
                    # self.bot.sendMessage(chat_ID, text="\n".join([f"{k}: {v} " for k,v in self.params.items()] ))
                    # self.bot.sendMessage(chat_ID, text=f"Thanks, {self.params['userName']}")
                    self.action()
                    self._exit()
                        
            else:
                print(colored(f"{self.action}\n{self.params}\n{self.to_know}\nUser:{self.user}", "white"))
                self.bot.sendMessage(chat_ID, message)
        else: #if is position
            print(msg["location"])
            self.params.update(msg["location"])
            self.to_know.pop(0)
            if self.to_know:
                self.bot.sendMessage(chat_ID, text=self.to_know[0])
            else:
                # self.bot.sendMessage(chat_ID, text="\n".join([f"{k}: {v} " for k,v in self.params.items()] ))
                # self.bot.sendMessage(chat_ID, text=f"Thanks, {self.params['userName']}")
                self.action()
                self._exit()
    
    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        print( "query", colored(f"{query_ID} {chat_ID} {query_data}","red"))
        if not "userID" in self.user:
            self.bot.sendMessage(chat_ID, text="Register or login first :)")
            self._exit(chat_ID)
            return

        if "insertHouse" in query_data:
            # self.action = "insertHouse"
            self.params={"uri":query_data ,"user_id":self.user["userID"] ,"chatID":chat_ID,"house_name":""}
            self.action = self.send_request
            self.to_know = ["house_name"]
            self.bot.sendMessage(chat_ID, text="Insert the house name:")
            
            
        if "insertRoom" in query_data:
            if len(self.user["houses"]) == 0:
                self.bot.sendMessage(chat_ID, text="Register a house first :)")
                return
            if len(self.user["houses"]) >1:
                buttons = [[InlineKeyboardButton(text=f"House {h['houseName']}", callback_data=f"insRoominHouse_{h['houseID']}") 
                                    for n,h in enumerate(self.houses)]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text="In which house?", reply_markup=keyboard)
                return
            else:
                query_data = "insRoominHouse_"+str(self.user["houses"][0]["houseID"])
        if "insRoominHouse" in query_data:
            self.params={"uri":"insertRoom" ,"user_id":self.user["userID"] , "house_id":query_data.split("_")[1]  , "roomName":"" }
            self.to_know = ["roomName"]
            self.action = self.send_request
            self.bot.sendMessage(chat_ID, text="Insert the room Name 🏡")
        
        if "insertPet" in query_data:
            if len(self.user["houses"]) == 0:
                self.bot.sendMessage(chat_ID, text="Register a house :)")
                return
            if len(self.user["houses"]) >1:
                buttons = [[InlineKeyboardButton(text=f"House {h['houseName']}", callback_data=f"insPetinHouse_{h['houseID']}") 
                                    for n,h in enumerate(self.houses)]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text="In which house?", reply_markup=keyboard)
                return
            else:
                query_data = "insPetinHouse_"+str(self.user["houses"][0]["houseID"])
        if "insPetinHouse" in query_data:
            self.params={"uri":"insertPet" ,"user_id":self.user["userID"] , "house_id":query_data.split("_")[1]  , "petName":"" }
            self.to_know = ["petName"]
            self.action = self.send_request
            self.bot.sendMessage(chat_ID, text="Insert the petName 🐶")
        
        if "insertDevice" in query_data:
            if len(self.user["houses"]) == 0:
                self.bot.sendMessage(chat_ID, text="Register a house :)")
                return
            if len(self.user["houses"]) >1:
                buttons = [[InlineKeyboardButton(text=f"House {h['houseName']}", callback_data=f"insDeviceinHouse_{h['houseID']}") 
                                    for n,h in enumerate(self.houses)]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text="In which house?", reply_markup=keyboard)
                return
            else:
                query_data = "insDeviceinHouse_"+str(self.user["houses"][0]["houseID"])
        if "insDeviceinHouse" in query_data:
            self.params={"uri":"insertDevice" ,"user_id":self.user["userID"] , "house_id":query_data.split("_")[1]  , "devicetype":"" , "ID" : None ,"ranges":[] }
            buttons = [[InlineKeyboardButton(text=d, callback_data=f"insDeviceType_{d}")]
                                for d in list(self.avail_devices.keys())]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text="Choose the device type", reply_markup=keyboard)
        if "insDeviceType" in query_data:
            devicetype = "_".join(query_data.split("_")[1:] )
            self.params["devicetype"] = devicetype
            house = [h for h in  self.houses if h["houseID"] == int(self.params["house_id"])][0]
            if devicetype.lower() == "collar":
                #choose a pet
                if len(house["petsList"]) ==0 :
                    self.bot.sendMessage(chat_ID, text="You should register a pet")
                    self._exit(chat_ID)
                    return 
                buttons = [[InlineKeyboardButton(text=p["petName"], callback_data=f"insDeviceID_{p['petID']}") ]
                                    for p in house["petsList"]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text="For which pet?", reply_markup=keyboard)
            else:
                #choose a room
                if len(house["roomsList"]) ==0 :
                    self.bot.sendMessage(chat_ID, text="You should register a room")
                    self._exit(chat_ID)
                    return
                buttons = [[InlineKeyboardButton(text=p["roomName"], callback_data=f"insDeviceID_{p['roomID']}") ]
                                    for p in house["roomsList"]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text="In which room?", reply_markup=keyboard)
        if "insDeviceID" in query_data:
            ID = query_data.split("_")[1] 
            self.params["ID"] = ID  
            self.bot.sendMessage(chat_ID, text=self.avail_devices[self.params["devicetype"]]["description"])
            if "to_know" in self.avail_devices[self.params["devicetype"]]:
                self.bot.sendMessage(chat_ID, text=self.avail_devices[self.params["devicetype"]]["to_know"][0])
                self.to_know = self.avail_devices[self.params["devicetype"]]["to_know"].copy()
                self.action = self.send_request
            else:
                self.send_request()
            
        if "delete" in query_data:
            tipo =  query_data.split("_")[1].lower()
            self.params={"uri": "delete","tipo" :tipo,"IDs":None}
            if tipo == "User":
                self.params["IDs"] = self.user["userID"]
                self.send_request() 
            else:
                if len(self.user["houses"]) == 0:
                    self.bot.sendMessage(chat_ID, text="Register a house first :)")
                    return
                if len(self.user["houses"]) >1:
                    buttons = [[InlineKeyboardButton(text=f'House {h["houseName"]}', callback_data=f"delHouse_{h['houseID']}") 
                                        for n,h in enumerate(self.houses)]]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text="In which house ?", reply_markup=keyboard)
                    return
                else:
                    query_data = "delHouse_"+str(self.user["houses"][0]["houseID"]  )               
            
        if "delHouse" in query_data:
            house_id =  int(query_data.split("_")[1])
            self.params["IDs"] = [self.user["userID"], house_id]
            h = [h for h in self.houses if h["houseID"] == house_id][0]
            if self.params["tipo"] == "house": 
                self.params["IDs"] = json.dumps(self.params["IDs"])
                self.send_request() 
                return
            elif self.params["tipo"] == "room":  
                if len(h["roomsList"]) == 0:
                    self.bot.sendMessage(chat_ID, text="Register a room first :)")
                    return
                if len(h["roomsList"]) >1:
                    buttons = [[InlineKeyboardButton(text=f'{r["roomName"]}', callback_data=f"delbyID_{r['roomID']}") 
                                        for n,r in enumerate(h["roomsList"])]]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text="Which room do you want to delete?", reply_markup=keyboard)
                    return
                else:
                    query_data = "delbyID_"+str(h["roomsList"][0]["roomID"] )
            elif self.params["tipo"] == "pet":  
                if len(h["petsList"]) == 0:
                    self.bot.sendMessage(chat_ID, text="Register a room first :)")
                    return
                if len(h["petsList"]) >1:
                    buttons = [[InlineKeyboardButton(text=f'{r["petName"]}', callback_data=f"delbyID_{r['petID']}") 
                                        for n,r in enumerate(h["petsList"])]]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text="Which pet do you want to delete?", reply_markup=keyboard)
                    return
                else:
                    query_data = "delbyID_"+str(h["petsList"][0]["petID"] )
            elif self.params["tipo"] == "device":  
                devices = []
                buttons = []
                for r in h["roomsList"]:
                    devices += r["devicesList"]
                    buttons += [[InlineKeyboardButton(text=f'🏡 {d["deviceName"]} ({r["roomName"]})', callback_data=f"delbyID_{d['deviceID']}")]
                                        for n,d in enumerate( r["devicesList"])]
                for p in h["petsList"]:
                    devices += p["devicesList"]
                    buttons += [[InlineKeyboardButton(text=f'🐶 {d["deviceName"]} ({p["petName"]})', callback_data=f"delbyID_{d['deviceID']}")]
                                        for n,d in enumerate( p["devicesList"])]
                if len(devices) == 0:
                    self.bot.sendMessage(chat_ID, text="Register a device first :)")
                    return
                if len(devices) >1:
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text="Which device do you want to delete?", reply_markup=keyboard)
                    return
                else:
                    query_data = "delbyID_"+str(devices[0]["deviceID"]) 
        if "delbyID" in query_data:
            id_last =  int(query_data.split("_")[1])
            self.params["IDs"] += [id_last]
            self.params["IDs"] = json.dumps(self.params["IDs"])
            self.send_request() 

        if "statistics" in query_data:
            print(query_data)
            self.params["nameid"] = query_data.split("_")[1]
            measureType = [query_data.split("_")[2]]
            if len(measureType) == 1:
                query_data = "stats_"+measureType[0]
            else:
                buttons = [[InlineKeyboardButton(text=types, callback_data=f"stats_{types}")]
                                    for types in measureType]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text="which stats do you want?", reply_markup=keyboard)
        if "stats" in query_data:
            self.params["measureType"] = query_data.split("_")[1]
            buttons = [[InlineKeyboardButton(text="Year", callback_data="startTime_years"), InlineKeyboardButton(text="Month", callback_data="startTime_months")],
                       [InlineKeyboardButton(text="Week", callback_data="startTime_weeks"), InlineKeyboardButton(text="Day", callback_data="startTime_days")]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text="History time report starts:", reply_markup=keyboard)
        if "startTime" in query_data:
            period = query_data.split("_")[1]
            time = pd.Timestamp("now")- eval(f"DateOffset({period}=1)")
            self.params["start"] = time.strftime('%Y.%m.%d.%H.%M.%S')
            self.params["userID"] = self.user["userID"]
            topic = "project/publish/statistics" 
            print(self.params)
            self.myPublish( topic, json.dumps(self.params))
            self.bot.sendMessage(chat_ID, text="Wait answer")
            self._exit()
            
        if "servToggle_" in query_data:
            self.params["pet_id"] = query_data.split("_")[1]
            self.send_request() 
    
    def send_request(self):
        self._preproces_params()
        print(self.params)
        x = requests.post(self.server_url+"/"+ self.params["uri"], data = self.params)
        print(colored(x.text,"green"))
        x = self._trasform_responde(x.text)
        if type(x) is str:
            if "chatID" in self.params:
                self.bot.sendMessage(self.params["chatID"], text=x)
            else:
                self.bot.sendMessage(self.user["chatID"], text=x)
        else:
            if "User" in self.params["uri"]:
                self.user.update(x)
                self.bot.sendMessage(self.user["chatID"], text=f"Welcome {self.user['userName']}")
                topic = f"project/alert/{self.user['userID']}/#"
                if self._paho:
                    self.mqtt_stop()
                self.inizializate_mqtt(self.user["userID"], self.port)
                self.mySubscribe(topic)
                
            if "statistics"  in self.params["uri"]:
                self.send_image(x)

            if "Room" in self.params["uri"]:
                self.bot.sendMessage(self.user["chatID"], text=f"✅ The room {self.params['roomName']} has succesfully been inserted")
            
            if "House" in self.params["uri"]:
                self.bot.sendMessage(self.user["chatID"], text=f"✅ The house {self.params['house_name']} has succesfully been inserted")
            
            if "Pet" in self.params["uri"]:
                self.bot.sendMessage(self.user["chatID"], text= f"✅ The pet {self.params['petName']} has succesfully been inserted")
            
            if "Device" in self.params["uri"]:
                self.bot.sendMessage(self.user["chatID"], text="✅ The insert has succesfully been inserted")
        self.update_user()
        self.action=None
        self.to_know = []
        self.params={}
        
    def _exit(self, chat_ID=False):
        self.action = None
        self.params={}
        self.to_know = []
        if chat_ID: self.bot.sendMessage(chat_ID, text="Azione annullata")
    
    def _trasform_responde(self,string):
        if type(string) is str:
            if "{" in string and "}" in string:
                return json.loads(string)
            string = string.replace('"',"")
        return string
    def _preproces_params(self):
        if "ranges" in self.params:
            self.params["ranges"] = self._bild_ranges(self.params)
        if "password" in self.params:
            self.params["password"] = hashlib.sha1(self.params["password"].encode()).hexdigest()
    def _bild_ranges(self,params):
        lis = eval(self.avail_devices[self.params["devicetype"]]["struct"])
        return json.dumps(lis)
    def update_user(self):
        x = requests.post(self.server_url+"/searchHousesbyUserID" , data ={"user_id":self.user["userID"]} )
        x = self._trasform_responde(x.text)
        self.houses = x
        x = requests.post(self.server_url+"/searchUserbyID" , data ={"user_id":self.user["userID"]} )
        x = self._trasform_responde(x.text)
        self.user = x

    def inizializate_mqtt(self,clientID,port):
        # print(clientID, self.broker, port)
        self._paho=pahoMqtt.Client(str(clientID),False)
        self._paho.on_message=self.myOnMessageReceived
        
        self._paho.connect(self.broker,port)
        self._paho.loop_start()
    def mqtt_stop(self):
        self._paho.loop_stop()
        self._paho.disconnect()
        self._paho = None
    
    def myOnMessageReceived(self, paho, userdata, msg):
        """
        topic: project/publish/*element*/*elementName*/*elementID*/*measurement*
            example: project/publish/room/bedroom/1/temperature
                     project/publish/pet/luca/1/heart_rate
         topics: temperature, mass_food, mass_water, heart_rate, respiration_rate, location
        """
        print(msg.payload.decode("utf-8"))
        #topic=msg.topic.split("/")
        message = json.loads(msg.payload)
        if "alert" in message:
            self.bot.sendMessage(self.user["chatID"], text=f"{message['alert']}")
        if "img" in message:
            self.bot.sendPhoto(self.user["chatID"], photo=open(message["img"], 'rb'))
        if "file" in message:
            self.bot.sendDocument(self.user["chatID"], document=open(message["file"], "rb"))
        print(colored(message,"magenta"))
    
    def mySubscribe(self,topic):
        self._paho.subscribe(topic,2)   
        print(colored("Subscribed to topic","magenta"),topic)
    
    def myPublish(self, topic, msg):
        self._paho.publish(topic, msg)
        print(colored(f"publish to {topic}","magenta"),colored(msg,"green"))
    
class Bot:
    exposed=True
    def __init__(self):    
        # Local token
        self.TOKEN = "1875569226:AAHT4PmBkCXbqHKhp1ggpf8iuwUJVCpVRc4"  # get token from command-line
        
        self.bot = telepot.DelegatorBot(self.TOKEN, [
        	include_callback_query_chat_id(
        		pave_event_space())(
        			per_chat_id(types='all'), create_open, InsertBot, timeout=600000),
        ])
        MessageLoop(self.bot).run_as_thread()
        print(colored("Bot Start","cyan"))


bot = Bot()

