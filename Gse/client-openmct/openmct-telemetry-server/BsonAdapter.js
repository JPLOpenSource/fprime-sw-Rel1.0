/*
    BsonAdapter.js

    Connect to the fprime tcp server on port 50000, deserialize binary and convert to JSON,
    then JSON to BSON, and then send them on to the openmct-telemetry-server on
    port 12345

    Author: Aaron Doubek-Kraft; aaron.doubek-kraft@jpl.nasa.gov
*/

var net = require('net');
var BSON = require('bson');

var deserialize = require('../server/src/deserialize').deserialize;
var config = require('../config.js').values();

var bson = new BSON();
var typeCodes = {
    I: 71,
    U: 72,
    F: 73,
    S: 74,
    E: 74
}

function BsonAdapter(target) {
    var self = this;
    this.target = target;

    //connect to the server at site:port, with the client passed as argument.
    //returns a promise so additional setup can be performed if operation was
    //successful
    function connectSocket(clientObj) {
        var port = clientObj.port,
            site = clientObj.site,
            client = clientObj.socket;

        return new Promise(function (resolve, reject) {
            client.connect(port, site, function () {
                    console.log(`BSON Adapter: Established connection to ${clientObj.name} on ${site}:${port}`);
                    resolve(true);
                });

            client.on('error', function (err) {
                reject(err.message);
            });
        });
    }

    // Take in the data as formatted for the openmct client, and convert it to
    // the format expected by the OpenMCT telemetry server
    function formatForOpenMCT(data) {
        formattedData = {
            timestamp: new Date(data.timestamp),
            identifier: data.id
        };
        if (data.type === 'channel') {
            formattedData.name = data.name;
            formattedData.raw_type = getBsonTypeCode(data.data_type);
            formattedData.raw_value = data.value;
        } else if (data.type === 'event') {
            formattedData.name = 'Events';
            formattedData.raw_type = getBsonTypeCode('S');
            formattedData.raw_value = data.name + ': ' + data.value;
        }

        return formattedData;
    }

    function getBsonTypeCode(data_type) {
        var typeCode = data_type.charAt(0);
        return typeCodes[typeCode];

    }

    function handleConnectionError(err) {
        console.log(`Connection Error: ${err}`);
        process.exit()
    }

    // connect to fprime server for input data, and socket on OpenMCT server
    // to push BSON data
    function setupConnections() {
        self.fprimeClient = {
            socket: new net.Socket(),
            name: "Fprime Telemetry Socket",
            port: config.tcpPort,
            site: config.tcpSite
        };
        self.openMCTTelemetryClient = {
            socket: new net.Socket(),
            name: "OpenMCT BSON Stream Socket",
            port: 12345,
            site: '127.0.0.1'
        };
        connectSocket(self.fprimeClient).then(function (success) {
            //fprime TCP server will not publish data until this message is sent
            self.fprimeClient.socket.write('Register GUI\n');
          }).catch(function (reject) {
              handleConnectionError(reject);
          });
        connectSocket(self.openMCTTelemetryClient).catch(function (reject) {
            handleConnectionError(reject);
        });
    };

    setupConnections();

    // event handler for recieving packets
    this.fprimeClient.socket.on('data', function (data) {
        var dataAsJSON = deserialize(data, self.target);

        dataAsJSON.forEach(function(datum) {
            var formattedDatum = formatForOpenMCT(datum);
            var dataAsBSON = bson.serialize(formattedDatum);
            self.openMCTTelemetryClient.socket.write(dataAsBSON);
        });
    });
}

module.exports = BsonAdapter;