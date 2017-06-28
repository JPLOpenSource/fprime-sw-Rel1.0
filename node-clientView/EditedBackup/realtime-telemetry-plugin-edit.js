/**
 * Basic Realtime telemetry plugin using websockets.
 */

var net = require('net');
function RealtimeTelemetryPlugin() {
    return function (openmct) {
        var socket = new net.Socket();
        socket.connect(8082, '127.0.0.1', function() {
            console.log('Connected!');

            // Register socket client
            // socket.write('Register GUI\n');
        })
        var listeners = {};

        socket.on('data', function(data) {
            point = JSON.parse(data);
            if (listeners[point.id]) {
                listeners[point.id].forEach(function (l) {
                    l(point);
                });
            }
        });

        var provider = {
            supportsSubscribe: function (domainObject) {
                return domainObject.type === 'example.telemetry';
            },
            subscribe: function (domainObject, callback, options) {
                if (!listeners[domainObject.identifier.key]) {
                    listeners[domainObject.identifier.key] = [];
                }
                if (!listeners[domainObject.identifier.key].length) {
                    socket.write('subscribe ' + domainObject.identifier.key);
                }
                listeners[domainObject.identifier.key].push(callback);
                return function () {
                    listeners[domainObject.identifier.key] =
                        listeners[domainObject.identifier.key].filter(function (c) {
                            return c !== callback;
                        });

                    if (!listeners[domainObject.identifier.key].length) {
                        socket.write('unsubscribe ' + domainObject.identifier.key);
                    }
                };
            }
        };

        openmct.telemetry.addProvider(provider);
    }
}