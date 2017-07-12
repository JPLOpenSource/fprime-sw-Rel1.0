/*
	Server used to translate tcp packet stream into mct format. Only works with one client atm.
*/

// Used to decode packets
var deserialize = require('./deserializeIsf.js').deserialize;

var net = require('net');
const WebSocket = require('ws');

function RealtimeIsfServer(site, isfPort, realMctPort) {

	// isf client
	var client = new net.Socket();
	client.connect(isfPort, site, function() {
		console.log('Connected!');

		// Register client
		client.write('Register GUI\n');
	})

	// Realtime webserver
	const wssr = new WebSocket.Server({port: realMctPort});

	// const wssh = new WebSocket.Server({port: 1338});

	var history = {};
	var clients = [];
	// For every client connection:
	wssr.on('connection', function connection(ws) {
		console.log("Realtime Client connected");

		var subscribed = {}; // Subscription dictionary
		clients = subscribed;

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
							console.log("Realtime Client disconnected", error);
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

// History server
// For every client connection:
// wssh.on('connection', function connection(ws) {
// 	console.log("Historical Client connected");

// 	// Subscription
// 	ws.on('message', function incoming(message) {
// 		var requested = JSON.parse(message);
// 		console.log("Req: ", message);
// 		var toSend = history[requested.id].filter(function (datum) {
// 			var start = requested.start;
// 			var end = requested.end;
// 			var query = parseInt(datum['timestamp'].toString().substring(0, start.toString().length));
// 			return query >= start && query <= end;
// 		});
// 		ws.send(JSON.stringify(toSend), function ack(error) {
// 			if (error) {
// 				// If unable to send (ie. client disconnection) then subscription is reset
// 				console.log("Historical Client disconnected", error);
// 			}
// 		});
// 	});  	
// });

// var express = require('express');

// server = express();
// HistMctPort = 1338;

// server.use(function (req, res, next) {
//     res.set('Access-Control-Allow-Origin', '*');
//     next();
// });

// server.get('/telemetry/:pointId', function (req, res) {
//     var start = +req.query.start;
//     var end = +req.query.end;
//     var ids = req.params.pointId.split(',');

//     var response = ids.reduce(function (resp, id) {
//         return resp.concat(history[id].filter(function (p) {
//             return parseInt(p.timestamp.toString().substring(0, 13)) > start && parseInt(p.timestamp.toString().substring(0, 13)) < end;
//         }));
//     }, []);
//     res.status(200).json(response).end();
// });

// server.listen(HistMctPort);
// console.log('History server now running at http://localhost:' + HistMctPort);

