
// Buffer
// Get dict
var dict = require('openmct-tutorial-installed/dictionary.json');

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
	console.log("Client connected");
	id_check = {};

	ws.on('message', function incoming(message) {
		var operation = message.split(" ")[0];	// Get subscribe or unsubscribe operation
	  	var idReq = message.split(" ")[1];	// Get id query
	  	console.log("ID: " + idReq);

	  	// Set id subscription
	  	if (operation == 'subscribe') {
	  		id_check[idReq] = true;
	  	} else if (operation == 'unsubscribe') {
	  		id_check[idReq] = false;
	  	}

	  	// Get isf data
		client.on('data', function(data) {

			// Decode data
			var ptr = 0;
			var size         = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
			var descriptor   = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
			var	id           = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
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
			// timestamp = parseInt((timeSeconds.toString()).concat((timeUSeconds.toString()).substring(0,3)), 10);
			timestamp = parseInt((timeSeconds.toString()).concat(timeUSeconds.toString()), 10);

			// Create datum in openMCT format
			var toMCT = {'timestamp':timestamp,'value':value,'id':id.toString()};
			console.log(toMCT);

			if (id_check[idReq] == true && idReq == id) {
				ws.send(JSON.stringify(toMCT));
			}
			
		});
	});

});


