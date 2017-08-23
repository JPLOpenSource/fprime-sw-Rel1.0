/**
 * Basic historical telemetry plugin. Local storage
 */

function HistoricalTelemetryPlugin(site, port) {
    return function install (openmct) {
        var provider = {
            supportsRequest: function (domainObject) {
                return domainObject.identifier.namespace === 'ref.taxonomy';
            },
            request: function (domainObject, options) {
                // Get log file
                return http.get('/server/logs/telem-log.json')
                    .then(function (result) {
                        return result.data[domainObject.identifier.key].filter(function (d) {
                            return d["timestamp"] > options.start && d["timestamp"] < options.end;
                        });
                });
            }
        };

        openmct.telemetry.addProvider(provider);
    }
}