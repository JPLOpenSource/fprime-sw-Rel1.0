/**
 * Basic Realtime telemetry plugin using websockets.
 */

var site = 'localhost'
var port = 1337;

function RealtimeTelemetryPlugin() {
    return function (openmct) {
        // Define what to do in this plugin:

        var socket = new WebSocket('ws://' + site + ':' + port.toString());
        var listeners = {}; // Dictionary of listeners

        // Get data
        socket.onmessage = function (event) {
            var point = JSON.parse(event.data); // Parse json data

            if (listeners[point.id]) {
                // If subscribed to telemetry based on 'id':
                listeners[point.id].forEach(function (l) {
                    l(point);
                });
            }
        };

        var provider = {
            // Must add 'supportsSubscribe' for realtime
            supportsSubscribe: function (domainObject) {
                // Subscribe to telemetry with given type
                return domainObject.type === 'isf.telemetry' || domainObject.type === 'isf.event';
            },
            subscribe: function (domainObject, callback, options) {
                if (!listeners[domainObject.identifier.key]) {
                    // Create array of datums if none found
                    listeners[domainObject.identifier.key] = [];
                }

                // If no array but want to subscribe, then send subscribe <telem stream>
                if (!listeners[domainObject.identifier.key].length) {
                    socket.send('subscribe ' + domainObject.identifier.key);
                }
                listeners[domainObject.identifier.key].push(callback);
                return function () {
                    // Return unsubscribe function:

                    listeners[domainObject.identifier.key] =
                        listeners[domainObject.identifier.key].filter(function (c) {
                            // Change array to only include values without callback
                            return c !== callback;
                        });

                    // Send unsub <telem stream> if no array. (Has been unsubscribed).
                    if (!listeners[domainObject.identifier.key].length) {
                        socket.send('unsubscribe ' + domainObject.identifier.key);
                    }
                };
            }
        };

        openmct.telemetry.addProvider(provider);
    }
}
