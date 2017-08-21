// Routes commands to net server.

var net = require('net');
const WebSocket = require('ws');	// Websocket server

var serialize = require('./serialize').serialize;

function CommandServer(site, gsePort, commandPort) {
	var client = new net.Socket();
	client.connect(gsePort, site, function() {
		console.log('Connected! Command server on port: ' + commandPort);

		fs.closeSync(fs.openSync('server/logs/command-log.json', 'w'));	// Create log json
		// Register client
		client.write('Register GUI\n');
	});

	// Command websocket listener
	const wssc = new WebSocket.Server({port: commandPort});

	wssc.on('connection', function connection(ws) {
		ws.on('message', function incoming(message) {
			// Save command to log
			fs.writeFile('server/logs/command-log.json', JSON.stringify(message), function (err) {
				if (err) {
					console.log(err);
				}
			});

			// Serialize message
			let commandPacket = serialize(JSON.parse(message));

			console.log(commandPacket);
			client.write(commandPacket);	// Send
		});
	});
}

module.exports = CommandServer;
