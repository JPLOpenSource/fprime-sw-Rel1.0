
// Buffer


var net = require('net');
const port = 50007;

var client = new net.Socket();
client.connect(port, '127.0.0.1', function() {
	console.log('Connected!');

	// Register client
	client.write('Register GUI\n');
})

client.on('data', function(data) {

	// Decode data
	var ptr = 0;
	const size         = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
	const descriptor   = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
	const id           = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
	const timeBase     = parseInt(data.toString('hex').substring(ptr, ptr += 4), 16);
	const timeContext  = parseInt(data.toString('hex').substring(ptr, ptr += 2), 16);
	const timeSeconds  = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
	const timeUSeconds = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
	const value 	   = parseInt(data.toString('hex').substring(ptr, (size + 4) * 2), 16);

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
});

