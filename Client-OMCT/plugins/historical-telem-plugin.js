/**
 * Basic historical telemetry plugin.
 */

function HistoricalTelemetryPlugin(site, port) {
    return function install (openmct) {
        var provider = {
            supportsRequest: function (domainObject) {
                return domainObject.identifier.namespace === 'isf.taxonomy';
            },
            request: function (domainObject, options) {
                // Query historical data point
                var url = 'http://' + site + ':' + port.toString() + 
                    '/telemetry/' +
                    domainObject.identifier.key +
                    '?start=' + options.start +
                    '&end=' + options.end;

                return http.get(url)
                    .then(function (resp) {
                        return resp.data;
                    });
            }
        };

        openmct.telemetry.addProvider(provider);
    }
}
