/*
    BsonAdapter.js

    Connect to the fprime tcp server on port 50000, deserialize binary and convert to JSON,
    then JSON to BSON, and then send them on to the openmct-telemetry-server on
    port 12345

    Author: Aaron Doubek-Kraft; aaron.doubek-kraft@jpl.nasa.gov
*/

var net = require('net');
var BSON = require('bson');

var deserialize = require('./util/deserialize-binary').deserialize;

var bson = new BSON();
var typeCodes = {
    I: 71,
    U: 72,
    F: 73,
    S: 74,
    E: 74
}

function BSONAdapter(target) {
    this.target = target;
    this.timeout = 5;

    this.fprimeClient = {
        socket: new net.Socket(),
        name: "Fprime Telemetry Socket",
        port: 50000,
        site: '127.0.0.1',
        successFunction: function (clientObj) {
            clientObj.socket.write('Register GUI\n');
        }
    };
    this.openMCTTelemetryClient = {
        socket: new net.Socket(),
        name: "OpenMCT BSON Stream Socket",
        port: 12345,
        site: '127.0.0.1',
        successFunction: function () {}
    };
}

BSONAdapter.prototype.run = function () {
    var self = this
    this.setupConnections()
    // event handler for recieving packets
    this.fprimeClient.socket.on('data', function (data) {
        var dataAsJSON = deserialize(data, self.target);

        dataAsJSON.forEach(function(datum) {
            var formattedDatum = self.formatForOpenMCT(datum);
            var dataAsBSON = bson.serialize(formattedDatum);
            self.openMCTTelemetryClient.socket.write(dataAsBSON);
        });
    });
}

// connect to fprime server for input data, and socket on OpenMCT server
// to push BSON data
BSONAdapter.prototype.setupConnections = function () {
    var self = this;
    this.connectSocket(this.fprimeClient).catch(function (reject) {
        console.log(`${self.fprimeClient.name}: Connection Error: ${reject}`);
        console.log(`${self.fprimeClient.name}: Attempting to reconnect every ${self.timeout} seconds`)
        self.handleConnectionError(reject, self.fprimeClient);
    });
    this.connectSocket(this.openMCTTelemetryClient).catch(function (reject) {
        console.log(`${self.openMCTTelemetryClient.name}: Connection Error: ${reject}`);
        console.log(`${self.openMCTTelemetryClient.name}: Attempting to reconnect every ${self.timeout} seconds`)
        self.handleConnectionError(reject, self.openMCTTelemetryClient);
  });
}

BSONAdapter.prototype.handleConnectionError = function (err, clientObj) {
    var self = this;

    setTimeout(function () {
        self.connectSocket(clientObj).catch(function (reject) {
            self.handleConnectionError(reject, clientObj)
        });
    }, self.timeout * 1000);
}

//connect to the server at site:port, with the client passed as argument.
//returns a promise so additional setup can be performed if operation was
//successful
BSONAdapter.prototype.connectSocket = function (clientObj) {
    var port = clientObj.port,
        site = clientObj.site,
        client = clientObj.socket,
        self = this;

    return new Promise(function (resolve, reject) {
        client.connect(port, site, function () {
            console.log(`BSON Adapter: Established connection to ${clientObj.name} on ${site}:${port}`);
            clientObj.successFunction(clientObj)
            resolve(true);
        });

        client.on('error', function (err) {
            client.removeAllListeners('error');
            client.removeAllListeners('connect')
            reject(err.message)
        });
    });
}

// Take in the data as formatted for the openmct client, and convert it to
// the format expected by the OpenMCT telemetry server
BSONAdapter.prototype.formatForOpenMCT = function(data) {
    formattedData = {
        timestamp: new Date(data.timestamp),
        identifier: data.id
    };
    if (data.type === 'channel') {
        formattedData.name = data.name;
        formattedData.raw_type = this.getBsonTypeCode(data.data_type);
        formattedData.raw_value = data.value;
    } else if (data.type === 'event') {
        formattedData.name = 'Events';
        formattedData.raw_type = this.getBsonTypeCode('S');
        formattedData.raw_value = data.name + ': ' + data.value;
    }

    return formattedData;
}

BSONAdapter.prototype.getBsonTypeCode = function (data_type) {
    var typeCode = data_type.charAt(0);
    return typeCodes[typeCode];
}

module.exports = BSONAdapter;
