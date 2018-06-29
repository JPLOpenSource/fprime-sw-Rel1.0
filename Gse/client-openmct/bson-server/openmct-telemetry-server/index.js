/**
 * Telemetry Server-- all configuration is passed in below.
 */

var TelemetryServer = require('./src/telemetry-server');
var config = require('./config');

var server = new TelemetryServer(config);

server.run();
