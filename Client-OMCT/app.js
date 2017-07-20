/**
 * Basic implementation of a history and realtime server.
 */

 var fs = require('fs');

var StaticServer = require('./server/static-server');
var RealtimeIsfServer = require('./server/telemetry-isf');
var HistoryIsfServer = require('./server/history-server');
var CreateFixed = require('./server/create-fixed');

const OMCTPort = 8080;
// Create static server for client
var staticServer = new StaticServer(OMCTPort);

// Initialize socket servers
const realMctPort = 1337;
const histMctPort = 1338;
const gsePort = 50000;
const site = '127.0.0.1';
RealtimeIsfServer(site, gsePort, realMctPort);
HistoryIsfServer(site, histMctPort);

CreateFixed();	// Generate fixed view from channels

// Handle exit
rmDir = function(dirPath, removeSelf) {
	if (removeSelf === undefined) {
		removeSelf = true;
	}
	try {
		var files = fs.readdirSync(dirPath);
	}
	catch(e) {
		return;
	}
	if (files.length > 0)
		for (var i = 0; i < files.length; i++) {
		  	var filePath = dirPath + '/' + files[i];
		  	if (fs.statSync(filePath).isFile())
		  	  fs.unlinkSync(filePath);
		  	else
		  	  rmDir(filePath);
		}
	if (removeSelf) {
	  fs.rmdirSync(dirPath);
	}
};

process.on('SIGINT', function () {
	console.log("Deleting temp files, cleaning up, and exiting");
	rmDir('./server/temp', false);
	process.exit();

});