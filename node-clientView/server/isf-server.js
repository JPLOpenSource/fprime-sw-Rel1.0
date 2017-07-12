// Server for openmct websocket

const realMctPort = 1337;
const isfPort = 50000;
const site = '127.0.0.1'

var RealtimeIsfServer = require('./realtime-isf');

RealtimeIsfServer(site, isfPort, realMctPort);
