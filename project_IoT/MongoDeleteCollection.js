var MongoClient = require('mongodb').MongoClient;

var url = "mongodb+srv://pi:raspberry@example.vjtls.mongodb.net?retryWrites=true&w=majority";

MongoClient.connect(url, function(err, db) {
    if (err) throw err;
    var dataBase_Name=process.argv[2]
    var collection_name=process.argv[3]
    // console.log(dataBase_Name)
    var dbo = db.db(dataBase_Name);


    dbo.collection(collection_name).drop(function(err, result){
        console.log("Error : "+err);
        if (err) throw err;
        console.log("Operation Success ? "+result);
        // after all the operations with db, close it.
        db.close();
        var ok=1;
        if (ok==1){
            process.exit();
        }
    });
    
});
