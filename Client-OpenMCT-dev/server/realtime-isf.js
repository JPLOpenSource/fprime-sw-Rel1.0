/*
	Server used to translate tcp packet stream into mct format. Only works with one client atm.
*/

// Used to decode packets
var deserialize = require('./deserializeIsf');

var net = require('net');
const WebSocket = require('ws');

function RealtimeIsfServer(site, gsePort, realMctPort) {

	// isf client
	var client = new net.Socket();
	client.connect(gsePort, site, function() {
		console.log('Connected! Realtime server on port: ' + realMctPort);

		// Register client
		client.write('Register GUI\n');
	})

	// Realtime webserver
	const wssr = new WebSocket.Server({port: realMctPort});

	// const wssh = new WebSocket.Server({port: 1338});

	var history = {};
	// For every client connection:
	wssr.on('connection', function connection(ws) {
		console.log("Realtime Client connected");

		var subscribed = {}; // Subscription dictionary

		// Get isf data
		client.on('data', function (data) {
			// Deserialize data into list of packets
			var toMCT = deserialize(data);

			// Send to websocket
			toMCT.forEach(function (packet) {
				// Add to history dictionary
				if (!history[packet.id]) {
					history[packet.id] = [];
				}
				history[packet.id].push(packet);

				// Send to realtime server
				if (subscribed[packet.id]) {
					ws.send(JSON.stringify(packet), function ack(error) {
						if (error) {
							// If unable to send (ie. client disconnection) then subscription is reset
							console.log("Realtime Client disconnected");
							subscribed = {};
						}
					});
				}
			})
		});

		// Subscription
		ws.on('message', function incoming(message) {
			var operation = message.split(" ")[0];	// Get subscribe or unsubscribe operation
		  	// Set id subscription
		  	if (operation === 'subscribe') {
		  		var idReq = message.split(" ")[1];	// Get id query
		  		subscribed[idReq] = true;
		  	} else if (operation === 'unsubscribe') {
		  		var idReq = message.split(" ")[1];	// Get id query
		  		subscribed[idReq] = false;
		  	}	
		});  	
	});
}

module.exports = RealtimeIsfServer;
