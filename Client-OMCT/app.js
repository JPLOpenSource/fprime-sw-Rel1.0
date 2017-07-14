/**
 * Basic implementation of a history and realtime server.
 */

var StaticServer = require('./server/static-server');
var RealtimeIsfServer = require('./server/telemetry-isf');

const OMCTPort = 8080;
// Create static server for client
var staticServer = new StaticServer(OMCTPort);

// Initialize socket servers
const realMctPort = 1337;
const histMctPort = 1338;
const gsePort = 50000;
const site = '127.0.0.1';
RealtimeIsfServer(site, gsePort, realMctPort);
