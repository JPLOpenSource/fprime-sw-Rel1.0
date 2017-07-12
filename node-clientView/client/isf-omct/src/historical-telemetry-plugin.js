/**
 * Basic historical telemetry plugin.
 */

HistMctPort = 1338;

function HistoricalTelemetryPlugin() {
    return function install (openmct) {
        var provider = {
            supportsRequest: function (domainObject) {
                return domainObject.type === 'isf.telemetry';
            },
            request: function (domainObject, options) {
                var url = 'http://localhost:' + HistMctPort.toString() + '/telemetry/' +
                    domainObject.identifier.key +
                    '?start=' + options.start +
                    '&end=' + options.end;

                return Promise.resolve([]);
                return http.get(url)
                    .then(function (resp) {
                        return resp.data;
                    });
            }
        };

        openmct.telemetry.addProvider(provider);
    }
}
