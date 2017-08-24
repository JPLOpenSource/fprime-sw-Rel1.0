/**
 * Basic implementation of a history and realtime server.
 */

// Dependencies
// Utils
var fs = require('fs');

// User Dependencies
var StaticServer = require('./src/static-server');
var RealtimeTelemServer = require('./src/telemetry-server');
var HistoryServer = require('./src/history-server');
var CommandServer = require('./src/command-server');
var CreateFixed = require('./src/create-fixed');


// Set following
const target = 'ref';   // Target Name
const nodeSite = '127.0.0.1';   // Host to serve the single page application
const OMCTPort = 8080;  // Port for single page application
const tcpSite = '127.0.0.1';    // Host of the TCP server
const tcpPort = 50000;  // Port for the TCP server
const realMctPort = 1337;   // Port streaming live telemetry datums to client
const commandPort = 1339;   // Port to listen for commands from client

// Create log directory
if (!fs.existsSync('server/logs')) {
    fs.mkdirSync('server/logs');
}

// Create static server for client
var staticServer = new StaticServer(OMCTPort);
RealtimeTelemServer(tcpSite, tcpPort, realMctPort, target);
HistoryServer();
CommandServer(tcpSite, tcpPort, commandPort, target);
