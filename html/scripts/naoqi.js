var NaoQiSession = function(ip){
  this.session = new QiSession(ip);

  this.session.socket().on('connect', function(){
    console.log("QiSession connected")
  }).on('disconnect', function(){
    console.log("QiSession disconnect");
  });

  return this;

}
