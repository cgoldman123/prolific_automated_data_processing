import gorilla = require("gorilla/gorilla");

//exp=169510; %Experiment id for Emotion Pictures_Updated_Prolific
// version=4;

gorilla.ready(() => {

    var mySetting = gorilla.retrieve(key:'correctAnswers', default:'NA');
})
