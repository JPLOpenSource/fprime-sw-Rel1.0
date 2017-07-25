// Routes commands to net server.

var net = require('net');
const WebSocket = require('ws');	// Websocket server

function CommandServer(site, gsePort, commandPort) {
	var client = new net.Socket();
	client.connect(gsePort, site, function() {
		console.log('Connected! Command server on port: ' + commandPort);
		// Register client
		client.write('Register GUI\n');
	});

	// Command websocket listener
	const wssc = new WebSocket.Server({port: commandPort});

	wssc.on('connection', function connection(ws) {
		ws.on('message', function incoming(message) {
			// Serialize message
			client.write(message);
		});
	});
}

module.exports = CommandServer;
