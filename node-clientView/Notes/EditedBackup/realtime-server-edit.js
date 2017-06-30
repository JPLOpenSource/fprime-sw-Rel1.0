var WebSocketServer = require('ws').Server;
var net = require('net');

function RealtimeServer(spacecraft, port) { // Delete spacecraft

    // ISF to node server tcp connection
    var client = new net.Socket();
    client.connect(50006, '127.0.0.1', function() {
        console.log('Connected!');
        // Register client
        client.write('Register GUI\n');
    })

    this.spacecraft = spacecraft;   // Delete spacecraft
    this.server = new WebSocketServer({ port: port });
    this.server.on('connection', this.handleConnection.bind(this));
    console.log('Realtime server started at ws://localhost:' + port);
};

RealtimeServer.prototype.handleConnection = function (ws) {
    var unlisten = this.spacecraft.listen(notifySubscribers);
    
        subscribed = {}, // Active subscriptions for this connection
        handlers = { // Handlers for specific requests
            subscribe: function (id) {
                subscribed[id] = true;
            },
            unsubscribe: function (id) {
                delete subscribed[id];
            }
        };

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
        const value        = parseInt(data.toString('hex').substring(ptr, (size + 4) * 2), 16);

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

    function notifySubscribers(point) {
        if (subscribed[point.id]) {
            ws.send(JSON.stringify(point));
        }
    }

    // Listen for requests
    ws.on('message', function (message) {
        var parts = message.split(' '),
            handler = handlers[parts[0]];
        if (handler) {
            handler.apply(handlers, parts.slice(1));
        }
    });

    // Stop sending telemetry updates for this connection when closed
    ws.on('close', unlisten);
};



module.exports = RealtimeServer;