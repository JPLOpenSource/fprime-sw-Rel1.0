/**
 * Basic implementation of a history and realtime server.
 */

 var fs = require('fs');

var StaticServer = require('./src/static-server');
var RealtimeIsfServer = require('./src/telemetry-isf');
var HistoryIsfServer = require('./src/history-server');
var CommandIsfServer = require('./src/command-isf');
var CreateFixed = require('./src/create-fixed');

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
// CommandIsfServer(site, gsePort, commandPort);

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
	rmDir('./temp', false);
	process.exit();

});