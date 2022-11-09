import paho.mqtt.client as pahoMqtt
import time
import json
from ms_comfort_room import comfort 
from ms_health import health
from ms_location import location
from ms_statistics import stats
import socket
# import sys
# import os
class subscriber():
    
    def __init__(self,clientID,broker,port):
        self.clientID=clientID
        self.broker=broker
        self.port=port
        self._paho=pahoMqtt.Client(self.clientID,False)
        self._paho.on_message=self.myOnMessageReceived
        
        self.urlCatalog=socket.gethostbyname(socket.gethostname())+":8090"

        # self.urlCatalog="http://192.168.43.127:8090"

        self.message=[]
        
        
    def start(self):
        self._paho.connect(self.broker,self.port)
        self._paho.loop_start()
    def stop(self):
        self._paho.loop_stop()
        self._paho.disconnect()
    
    def myOnMessageReceived(self, paho, userdata, msg):
        # print("si")
        """
        topic: project/publish/*element*/*elementName*/*elementID*/*measurement*
            example: project/publish/room/bedroom/1/temperature
                     project/publish/pet/luca/1/heart_rate
         topics: temperature, mass_food, mass_water, heart_rate, respiration_rate, location
        """
        
        
        topic=msg.topic.split("/")
        message = json.loads(msg.payload)
        # print(f"topic: {topic}")    
        ans=None
        # print(message)
        if (topic[2]=="room" and topic[1]=="publish"):
            if topic[5] =="temperature":
                ans = comfort(self.urlCatalog,topic[4]).temperature(message)
            elif topic[5] == "mass_food":
                ans = comfort(self.urlCatalog,topic[4]).mass("food",message)
            elif topic[5] == "mass_water":
                ans = comfort(self.urlCatalog,topic[4]).mass("water",message)

        elif (topic[2]=="pet" and topic[1]=="publish"):
            # print("pet")
            if topic[5] == "heart_rate": 
                ans=health(self.urlCatalog,topic[4]).heart_rate(message)
                
            elif topic[5] == "respiration_rate": 
                ans=health(self.urlCatalog,topic[4]).respiration_rate(message)   
                
            elif topic[5] == "location":
                ans=location(self.urlCatalog,topic[4]).control_position(message)
                
            
            elif topic[5] == "basal_temperature":
                ans=health(self.urlCatalog,topic[4]).basal_temperature(message)
               
        elif("statistics" in topic):
             ans=stats("http://"+self.urlCatalog).stats_for(message)   

             
            

        if ans!=None: 
            self.myPublish(ans[0], json.dumps(ans[1]))
            # print(ans)
            print(ans[1]["alert"])
        
    
    def mySubscribe(self,topic):
        self._paho.subscribe(topic,2)
        
    def myPublish(self, topic, msg):
        # filename = "catalogo.json"
        # with open(filename) as f:
        #     file=json.load(f)
            
        # #se l'alert riguarda il pet (collar):    
        # if topic.split("/")[2] == "pet":
        #     for house in file["houses"]:
        #         for pet in house["petsList"]:
        #             if pet["Activateservices"] == True and pet["petID"] == topic.split("/")[4]: 
        #                 # if the pet is in the house the alert from the collar are sent
        #                 self._paho.publish(topic, msg)
        # else: # topic.split("/")[2] == "room"
            
        #     petinhouse = False
        #     for house in file["houses"]:
        #         for room in file["roomsList"]:
        #             if room["roomID"] == topic.split("/")[4]:
        #                 for pet in house["petsList"]:
        #                     if pet["Activateservices"] == True:
        #                         petinhouse = True
        #     if petinhouse == True:
        #         self._paho.publish(topic, msg)
        self._paho.publish(topic, msg)
                
                
if __name__ == '__main__':
    try:
        dev=subscriber("Server_mqtt","mqtt.eclipseprojects.io",1883)
        dev.start()
        dev.mySubscribe("project/publish/#")
        # dev.mySubscribe("project/#")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print('Interrupted')
        dev._paho.unsubscribe("project/#")
        dev.stop()
    