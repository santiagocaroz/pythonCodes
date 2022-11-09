var mqtt = require('mqtt')
var MongoClient = require('mongodb').MongoClient;
var url = "mongodb+srv://pi:raspberry@example.vjtls.mongodb.net?retryWrites=true&w=majority";
const options = {
  // Clean session
  clean: true,
  connectTimeout: 4000,
  // Auth
  clientId: 'servizi',
}
var client  = mqtt.connect("mqtt://mqtt.eclipseprojects.io:1883",options)

// on mqtt conect subscribe on tobic test 
client.on('connect', function () {
  client.subscribe('project/publish/#', function (err) {
      if(err)
      console.log(err)
  })
})

var topic_elements

 //when recive message 
client.on('message', function (topic, message) {
  json_check(message)
  console.log(JSON.parse(message))
  topic_elements=topic.split("/")

  // console.log(topics)
  
})

// check if data json or not

function json_check(data) {
    try {
        JSON.parse(data);
    } catch (e) {
        return false;
    }
    Mongo_insert(JSON.parse(data))
}


function Mongo_insert(data){
MongoClient.connect(url, function(err, db ) {
    if (err) throw err;
    var dbo = db.db(topic_elements[3]+topic_elements[4]);
    dbo.collection(topic_elements[5]).insertOne(data, function(err, res) {
      if (err) throw err;
      console.log("1 document inserted");
      db.close();
    });
  }); 
}