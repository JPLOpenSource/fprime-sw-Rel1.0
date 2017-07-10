/*
	Server used to translate tcp packet stream into mct format. Only works with one client atm.
*/

// Used to decode packets
var deserialize = require('./deserializeIsf.js').deserialize;

var net = require('net');
const WebSocket = require('ws');

const mct_port = 1337;
const isf_port = 50000;

// isf client
var client = new net.Socket();
client.connect(isf_port, '127.0.0.1', function() {
	console.log('Connected!');

	// Register client
	client.write('Register GUI\n');
})

const wss = new WebSocket.Server({port: 1337});

var clients = [];
// For every client connection:
wss.on('connection', function connection(ws) {
	console.log("Client connected");

	var subscribed = {}; // Subscription dictionary
	clients = subscribed;

	// Get isf data
	client.on('data', function (data) {
		// Deserialize data into list of packets
		var toMCT = deserialize(data);

		// Send to websocket
		toMCT.forEach(function (packet) {
			if (subscribed[packet.id]) {
				ws.send(JSON.stringify(packet), function ack(error) {
					if (error) {
						// If unable to send (ie. client disconnection) then subscription is reset
						console.log("Client disconnected", error);
						// subscribed = {};	// Reset subscription dictionary
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


