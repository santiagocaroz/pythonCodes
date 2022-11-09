# -*- coding: utf-8 -*-
"""
Created on Thu May  5 10:24:44 2022

@author: Santiago Caro
"""
import requests
import json
import time
import os
from datetime import datetime 


class client:
    
    
    def __init__(self):
        self.session = requests.Session()
        self.url = "https://data.mongodb-api.com/app/data-ftwdf/endpoint/data/beta/action/"
        self.headers = {"Content-Type":"application/json","Access-Control-Request-Headers":"*","api-key":"9HJF3YMr4A0pi6vPDTfEN0uZYGfMsQLuzoxKk9C8Fc1WQjVnB8AoVLNQ0V4Cakhq"}
       
    
    def insertDatabase(self, database_name):
        database_name="_".join(database_name.split())
        data={
            "dataSource": "Example",
            "database": database_name,
            "collection": "Init",
            "document":{    
            }
            }
        post = self.session.post(self.url+"insertOne", json = data,headers=self.headers)
        
        return post.text
    def insertCollection(self,database_name,collection):
        database_name="_".join(database_name.split())
        collection="_".join(collection.split())
        data={
            "dataSource": "Example",
            "database": database_name,
            "collection": collection,
            "document":{    
            }
            }
        post = self.session.post(self.url+"insertOne", json = data,headers=self.headers)
        time.sleep(1)
        self.deleteAllDocuments(database_name,collection)
        
        
    def deleteDatabase(self,database_name):
        database_name="_".join(database_name.split())
        os.system('cmd /k "node MongoDeleteDatabase.js '+database_name+'"')
    
    def deleteCollection(self,database_name, collection):
        database_name="_".join(database_name.split())
        collection="_".join(collection.split())
        os.system(f'cmd /k "node MongoDeleteCollection.js {database_name} {collection}"')
        
    def deleteAllDocuments(self, database_name,collection):
        database_name="_".join(database_name.split())
        collection="_".join(collection.split())
        data={
            "dataSource": "Example",
            "database": database_name,
            "collection": collection,
            "filter":{} #Select everything
                
            }
        post = self.session.post(self.url+"deleteMany", json = data,headers=self.headers)
        return post.text
    def searchbyTime(self,database_name,collection,time):
        """
            

        Parameters
        ----------
        database_name : String
            Name of pet or room with ID, ex. Luna1, kitchen3
        collection : String
            name measure, ex. temperature, mass_water 
        time : Array
            time=[from when, to when ]
            time=["YYYY.MM.DD.HH.MM.SS", "YYYY.MM.DD.HH.MM.SS"]
            time=["YYYY.MM.DD.HH.MM.SS", "now"]

        Returns
        -------
        
        """
        if time[1]=="now":
            time[1]=datetime.now().strftime("%Y.%m.%d.%H.%M.%S")
        database_name="_".join(database_name.split())
        collection="_".join(collection.split())
        data={
              "dataSource": "Example",
              "database": database_name,
              "collection": collection,
              "pipeline": [
              
              {"$match":{"time":{"$gt":time[0],"$lt":time[1]},collection:{"$exists":"true"}}},
              {"$sort": { "time":1  }}
              ]
          }
        post = self.session.post(self.url+"aggregate", json = data,headers=self.headers)
        return json.loads(post.text)
        
if __name__ == '__main__':
    
    cl=client()
    
        