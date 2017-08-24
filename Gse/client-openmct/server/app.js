/**
 * Basic implementation of a history and realtime server.
 */

var fs = require('fs');

var StaticServer = require('./src/static-server');
var RealtimeTelemServer = require('./src/telemetry-server');
var HistoryServer = require('./src/history-server');
var CommandServer = require('./src/command-server');
var CreateFixed = require('./src/create-fixed');

// Create temp directory
if (!fs.existsSync('server/logs')) {
    fs.mkdirSync('server/logs');
}

const OMCTPort = 8080;
// Create static server for client
var staticServer = new StaticServer(OMCTPort);

// Initialize socket servers
const realMctPort = 1337;
const histMctPort = 1338;
const commandPort = 1339;
const tcpPort = 50000;
const nodeSite = '127.0.0.1';
const tcpSite = '127.0.0.1';
const target = 'ref';

RealtimeTelemServer(tcpSite, tcpPort, realMctPort, target);
HistoryServer(nodeSite, histMctPort);
CommandServer(tcpSite, tcpPort, commandPort, target);
