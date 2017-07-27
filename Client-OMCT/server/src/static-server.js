var express = require('express');
function StaticServer(port) {
    var server = express();
    
    server.use('/', express.static(__dirname + '/../../index-dev.html'));
    
    console.log('Open MCT hosted at http://localhost:' + port);
    
    server.listen(port);
}

module.exports = StaticServer;
