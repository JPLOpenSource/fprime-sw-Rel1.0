/*
	Server used to translate tcp packet stream into mct format. Only works with one client atm.
*/


// Get dict
var dict = require('../client/isf-omct/res/dictionary.json');

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

subscribed = {};	// Subscription dictionary
var num_format = {};	// Save formats of each id
// For every client connection:
wss.on('connection', function connection(ws) {
	console.log("Client connected");

	// Get isf data
	client.on('data', function (data) {

		// Decode data
		var ptr = 0;
		var size         = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var descriptor   = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var	id           = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		if (subscribed[id]) {
			// Check if id is in subscription dictionary to continue decoding data
			var timeBase     = parseInt(data.toString('hex').substring(ptr, ptr += 4), 16);
			var timeContext  = parseInt(data.toString('hex').substring(ptr, ptr += 2), 16);
			var timeSeconds  = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
			var timeUSeconds = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);

			var telem = dict.measurements;	// List of telemetry dictionary data
			var telemSize = dict.measurement_size;
			
			if (!(id in num_format)) {
				console.log("New id: " + id);
				// If not saved in num_format dictionary, find format for id
				var telem = dict.measurements;	// List of telemetry dictionary data
				var telemSize = dict.measurement_size;
				for (i = 0; i < telemSize; i++) {
					if (id.toString() === telem[i].key) {
						num_format[id] = telem[i].num_type;
					}
				}
			}

			// Check if floating point conversion is needed
			if (num_format[id].indexOf("F") != -1) {
				var hexValue = data.toString('hex').substring(ptr, (size + 4) * 2);	// Get value

				// Convert to float
				var dv = new DataView(new ArrayBuffer(8));
				dv.setUint32(0, parseInt("0x" + hexValue));
				var value = dv.getFloat32(0);
			} else {
				// Get value from packet if no conversion is needed
				var value = parseInt(data.toString('hex').substring(ptr, (size + 4) * 2), 16);
			}

			timestamp = parseInt((timeSeconds.toString()).concat(timeUSeconds.toString()), 10);

			// Create datum in openMCT format
			var toMCT = {'timestamp':timestamp,'value':value,'id':id.toString()};

			// Print/debug
			console.log(toMCT);

			// Send to websocket
			ws.send(JSON.stringify(toMCT), function ack(error) {
				if (error) {
					// If unable to send (ie. client disconnection) then subscription is reset
					console.log("Client disconnected");
					subscribed = {};
				}
			});
		}
		
	});

	// Subscription
	ws.on('message', function incoming(message) {
		var operation = message.split(" ")[0];	// Get subscribe or unsubscribe operation
	  	var idReq = message.split(" ")[1];	// Get id query
	  	console.log("ID: " + idReq);

	  	// Set id subscription
	  	if (operation == 'subscribe') {
	  		subscribed[idReq] = true;
	  	} else if (operation == 'unsubscribe') {
	  		subscribed[idReq] = false;
	  	}	
	});  	
});


