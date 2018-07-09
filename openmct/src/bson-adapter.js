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

function BSONAdapter(config) {

    this.target = config.binaryInput.deployment;

    // Frequency, in seconds, with which the adapter polls a socket when
    // attempting to connect.
    this.timeout = 5;

    console.log(`Using deployment key '${this.target}' \n`)

    this.fprimeClient = {
        socket: new net.Socket(),
        name: "Fprime Telemetry Socket",
        port: config.binaryInput.port,
        site: config.binaryInput.bindAddress,
        successFunction: function () {
            // ThreadedTCPServer will not send packets until it recieves this command
            this.socket.write('Register GUI\n');
        }
    };

    this.openMCTTelemetryClient = {
        socket: new net.Socket(),
        name: "OpenMCT BSON Stream Socket",
        port: config.input.port,
        site: config.input.bindAddress,
        successFunction: function () {}
    };

}

BSONAdapter.prototype.run = function () {

    this.setupConnections()

    // event handler for recieving packets
    this.fprimeClient.socket.on('data', (data) => {
        var dataAsJSON = deserialize(data, this.target);

        dataAsJSON.forEach( (datum) => {
            var datumAsBSON = bson.serialize(datum);
            this.openMCTTelemetryClient.socket.write(datumAsBSON);
        });
    });

}

// connect to fprime server for input data, and socket on OpenMCT server
// to push BSON data
BSONAdapter.prototype.setupConnections = function () {

    this.connectSocket(this.fprimeClient).catch( (reject) => {
        console.log(`${this.fprimeClient.name}: Connection Error: ${reject}`);
        console.log(`${this.fprimeClient.name}: Attempting to reconnect every ${this.timeout} seconds`)
        this.handleConnectionError(reject, this.fprimeClient);
    });

    this.connectSocket(this.openMCTTelemetryClient).catch( (reject) => {
        console.log(`${this.openMCTTelemetryClient.name}: Connection Error: ${reject}`);
        console.log(`${this.openMCTTelemetryClient.name}: Attempting to reconnect every ${this.timeout} seconds`)
        this.handleConnectionError(reject, this.openMCTTelemetryClient);
    });

}

BSONAdapter.prototype.handleConnectionError = function (err, clientObj) {

    setTimeout( () => {
        this.connectSocket(clientObj).catch( (reject) => {
            this.handleConnectionError(reject, clientObj)
        });
    }, this.timeout * 1000);

}

//connect to the server at site:port, with the client passed as argument.
//returns a promise so additional setup can be performed if operation was
//successful
BSONAdapter.prototype.connectSocket = function (clientObj) {

    var port = clientObj.port,
        site = clientObj.site,
        client = clientObj.socket;

    return new Promise( (resolve, reject) => {
        client.connect(port, site, () => {
            console.log(`BSON Adapter: Established connection to ${clientObj.name} on ${site}:${port}`);
            clientObj.successFunction(clientObj)
            resolve(true);
        });

        client.on('error', (err) => {
            client.removeAllListeners('error');
            client.removeAllListeners('connect')
            reject(err.message)
        });
    });

}

module.exports = BSONAdapter;
