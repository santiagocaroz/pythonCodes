1. CatalogServer.py: run this script to start the server.
It contains all the REST methods to communicate with the Catalog
	1.1 catalog_manager.py: contains the methods to manipulate data of the catalog..1
	These methods are used by the Catalog Server
		1.1.1 MongoDeleteCollection.js: Contain the function to delete a collection from mongoDB, It is runned inside the catalog_manager.py
		1.1.2 MongoDeleteDatabase.js:Contain the function to delete a database from mongoDB, It is run inside the catalog_manager.py
		1.1.3 client_mongoDB.py: Contain the methods to create databases and collections, and also to search data i

2. subscriber_mqtt.py: run this script to activate microservices.
It is a subscriber and a publisher for the microservices:
	2.1 ms_health.py
	2.2 ms_location.py
	2.3 ms_comfort_room.py
	2.4 ms_statistics.py

3.BotTelegram_chat.py: run this script to activate the Telegram Bot.
It communicates with subscriber_mqtt.py and with Catalog.Server.py

4.mqttNode.js: run this script using the command prompt with the command "node mqttNode.js" to subscribe the topics "project/publish/#" and then
save this data in MongoDB

5.NodeRED-Raspberry-simulation.json: Contain a copy of the flows that are running in the raspberry. When is run it generates the measurements and pusblish
them with topics "project/publish/*element*/*elementName*/*elementID*/*measure*/". And also subscribe the topic "project/alert/#" to active actuators 
when is needed

--- OTHER FILES ---
- catalogo.json: a draft of a possible catalog
- data.csv: contains the data simulated for heart rate and respiration rate. 
We assume that they are provided in this form from the simulated sensor



