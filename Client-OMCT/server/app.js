/**
 * Basic implementation of a history and realtime server.
 */

var fs = require('fs');

var StaticServer = require('./src/static-server');
var RealtimeServer = require('./src/telemetry-isf');
var HistoryServer = require('./src/history-server');
var CommandServer = require('./src/command-isf');
var CreateFixed = require('./src/create-fixed');

// Create temp directory
if (!fs.existsSync('server/logs')) {
    fs.mkdirSync('server/logs');
}

if (!fs.existsSync('server/command-log')) {
    fs.mkdirSync('server/command-log');
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

RealtimeServer(site, gsePort, realMctPort);
HistoryServer(site, histMctPort);
CommandServer(site, gsePort, commandPort);
