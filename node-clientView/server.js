
// Buffer


var net = require('net');
const WebSocket = require('ws');

const mct_port = 1337;
const isf_port = 50006;

// isf client
var client = new net.Socket();
client.connect(isf_port, '127.0.0.1', function() {
	console.log('Connected!');

	// Register client
	client.write('Register GUI\n');
})

const wss = new WebSocket.Server({port: 1337});

wss.on('connection', function connection(ws) {

	// Get isf data
	var toMCT;
	var id;
	client.on('data', function(data) {

		// Decode data
		var ptr = 0;
		var size         = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var descriptor   = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
			id           = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var timeBase     = parseInt(data.toString('hex').substring(ptr, ptr += 4), 16);
		var timeContext  = parseInt(data.toString('hex').substring(ptr, ptr += 2), 16);
		var timeSeconds  = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var timeUSeconds = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var value 	     = parseInt(data.toString('hex').substring(ptr, (size + 4) * 2), 16);

		// Print data
		console.log('Received: ' + 
			size + ',' + 
			descriptor + ',' + 
			id + ',' + 
			timeBase + ',' + 
			timeContext + ',' + 
			timeSeconds + ',' + 
			timeUSeconds + ',' + 
			value
			);

		toMCT = {"timestamp":timeSeconds,"value":value,"id":id}

		console.log(toMCT);
	});

	ws.on('message', function incoming(message) {
	  	var idReq = message.split(" ")[1];
	  	console.log("ID: " + idReq);

		if (idReq == id) {
			ws.send(JSON.stringify(toMCT));
		}
	});

});


