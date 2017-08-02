/**
 * Basic implementation of a history and realtime server.
 */

var fs = require('fs');

var StaticServer = require('./src/static-server');
var RealtimeIsfServer = require('./src/telemetry-isf');
var HistoryIsfServer = require('./src/history-server');
var CommandIsfServer = require('./src/command-isf');
var CreateFixed = require('./src/create-fixed');

// Create temp directory
if (!fs.existsSync('server/temp')) {
    fs.mkdirSync('server/temp');
}

const OMCTPort = 8080;
// Create static server for client
var staticServer = new StaticServer(OMCTPort);

// Initialize socket servers
const realMctPort = 1337;
const histMctPort = 1338;
const commandPort = 1339;
const gsePort = 50000;
const site = '127.0.0.1';

RealtimeIsfServer(site, gsePort, realMctPort);
HistoryIsfServer(site, histMctPort);
CommandIsfServer(site, gsePort, commandPort);
