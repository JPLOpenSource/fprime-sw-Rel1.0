/**
 * Basic implementation of a history and realtime server.
 */

var StaticServer = require('./server/static-server');
var RealtimeIsfServer = require('./server/realtime-isf');

// Create static server for client
var staticServer = new StaticServer(8080);

// Initialize socket servers
const realMctPort = 1337;
const gsePort = 50000;
const site = '127.0.0.1';
RealtimeIsfServer(site, gsePort, realMctPort);
