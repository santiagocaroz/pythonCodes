# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 17:01:13 2022

@author: Santiago Caro
"""

import cherrypy
import json
import catalog_manager as catalog
import socket
from termcolor import colored


class CatalogServer:
    #Vecchio
    exposed=True
    def __init__(self,filename):
        self.filename=filename
        self.catalogo=catalog.Catalog(self.filename)
    
    def GET(self, *uri,**params):
        if uri[0] == "searchHousesbyUserID":
            avail_params = ["user_id"]
        elif uri[0] == "searchUserbyID":
            avail_params = ["user_id"]
        elif uri[0] == "searchUserbyName_Psw":
            avail_params = ["userName","password"]
        elif uri[0] == "statistics":
            avail_params = ["nameid","measureType","start"]
        else:
            avail_params = ["user_id","house_id","ID","pet_id","room_id","idx","img"]
        print("self.catalogo."+uri[0]+"("+ ",".join([f" {b}={c} " for b,c in params.items() if b in avail_params])       +")")
        a = eval("self.catalogo."+uri[0]+"("+ ",".join([f" {b}={c} " for b,c in params.items() if b in avail_params])       +")")
        return json.dumps(a)


        
        
    def POST(self,*uri,**params):

        if   uri[0] == "insertUser":
            avail_params = ["userName","password", "chatID"]
        elif uri[0] == "insertHouse":
            avail_params = ["house_name", "user_id"]
        elif uri[0] == "insertRoom" or uri[0] == "insertPet":
            avail_params = ["user_id","house_id","roomName","petName"]
        elif uri[0] == "insertDevice":
            avail_params = ["user_id","house_id","ID","devicetype","ranges"]
        elif uri[0] == "searchHousesbyUserID":
            avail_params = ["user_id"]
        elif uri[0] == "searchUserbyID":
            avail_params = ["user_id"]
        elif uri[0] == "update_Activateservices":
            avail_params = ["pet_id"]
        elif uri[0] == "searchUserbyName_Psw":
             avail_params = ["userName","password"]
        elif uri[0] == "delete":
            avail_params = ["tipo","IDs"]
        elif uri[0] == "statistics":
            avail_params = ["nameid","measureType","start"]
        else:
            return "Not avaible uri"
        # print(uri, params)
        print(colored("self.catalogo."+uri[0]+"("+ ",".join([f" {b}='{c}' " for b,c in params.items() if b in avail_params])       +")" ,"cyan"))
        a =  eval("self.catalogo."+uri[0]+"("+ ",".join([f" {b}='{c}' " for b,c in params.items() if b in avail_params])       +")")
        return json.dumps(a)
    


    
    def PUT(self,*uri,**params):
        data=json.loads(cherrypy.request.body.read().decode())
        # print(json.loads(data))

        eval("self.catalogo."+uri[0]+"("+"'"+params["tipo"]+"',"+params["ID"]+","+str(data)+")")
        return "Done"
    

    def DELETE(self,*uri,**params):
        avail_params = ["tipo","IDs"]
        print(colored("self.catalogo."+uri[0]+"("+ ",".join([f" {b}='{c}' " for b,c in params.items() if b in avail_params])       +")" ,"cyan"))
        a =  eval("self.catalogo."+uri[0]+"("+ ",".join([f" {b}='{c}' " for b,c in params.items() if b in avail_params])       +")")
        return json.dumps(a)        
    
    
    
if __name__ == '__main__':
    ip=socket.gethostbyname(socket.gethostname())
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,       
        },

        'global':{"server.socket_port":8090,
                  "server.socket_host": ip}

    }
    cherrypy.tree.mount(CatalogServer("catalogo.json"),"/",conf)
    # cherrypy.config.update({"server.socket_port":9090})
    cherrypy.config.update(conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
