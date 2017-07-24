/*
	Server used to translate tcp packet stream into mct format. Only works with one client atm.
*/

// Used to decode packets
var fs = require('fs');
var deserialize = require('./deserializeIsf').deserialize;
var getIds = require('./deserializeIsf').getIds;

var net = require('net');
const WebSocket = require('ws');

var history = {};
function RealtimeIsfServer(site, gsePort, realMctPort) {

	// isf client
	var client = new net.Socket();
	client.connect(gsePort, site, function() {
		console.log('Connected! Realtime server on port: ' + realMctPort);

		// Register client
		client.write('Register GUI\n');

		// Populate history with ids
		getIds().forEach(function (id) {
			history[id.toString()] = [];
		});

	});

	// Realtime webserver
	const wssr = new WebSocket.Server({port: realMctPort});

	// Get isf data and save to history
	client.on('data', function (data) {
		// Deserialize data into list of packets
		var toMCT = deserialize(data);

		// Send to websocket
		toMCT.forEach(function (packet) {
			// Add to history dictionary
			history[(packet.id).toString()].push(packet);
			fs.writeFile('server/temp/log.json', JSON.stringify(history), function (err) {
				if (err) {
					console.log(err);
				}
			});
		
		});
	});


	wssr.on('connection', function connection(ws) {
		// For every client connection:
		console.log("Realtime Client connected");

		var subscribed = {}; // Subscription dictionary unique to each connected client

		// Get isf data and send realtime telem data
		client.on('data', function (data) {
			// Deserialize data into list of packets
			var toMCT = deserialize(data);

			// Send to websocket
			toMCT.forEach(function (packet) {
				// Add to history dictionary

				// Send to realtime server
				if (subscribed[packet.id]) {
					ws.send(JSON.stringify(packet), function ack(error) {
						if (error) {
							// If unable to send (ie. client disconnection) 
							// then subscription is reset
							console.log("Realtime Client disconnected");
							subscribed = {};
						}
					});
				}
			});
		});

		// Subscription
		ws.on('message', function incoming(message) {
			var operation = message.split(" ")[0];	// Get subscribe or unsubscribe operation
			var idReq = message.split(" ")[1];	// Get id query
		  	// Set id subscription
		  	if (operation === 'subscribe') {
		  		// Subscribe to id
		  		subscribed[idReq] = true;
		  	} else if (operation === 'unsubscribe') {
		  		// Unsubscribe to id
		  		subscribed[idReq] = false;
		  	}	
		});  	
	});
}

module.exports = RealtimeIsfServer;