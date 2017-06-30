/**
 * Basic historical telemetry plugin.
 */

function HistoricalTelemetryPlugin() {
    return function install (openmct) {
        var provider = {
            // 'supportsRequest' must be used for historical telemetry
            supportsRequest: function (domainObject) {
                return domainObject.type === 'example.telemetry';
            },
            // returns array of telemetry datums fullfilling the request.
            request: function (domainObject, options) {
                // Query telemetry
                var url = 'http://localhost:8081/telemetry/' +
                    domainObject.identifier.key +
                    '?start=' + options.start +
                    '&end=' + options.end;

                return http.get(url).then(function (resp) {
                    return resp.data;
                });
            }
        };

        openmct.telemetry.addProvider(provider);
    }
}
