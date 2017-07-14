/**
 * Basic historical telemetry plugin.
 */

function getDictionary() {
    // Needs directory from root of application
    return http.get('/plugins/dictionary.json').then(function (result) {
        return result.data;
    });
}

function HistoricalTelemetryPlugin() {
    return function install (openmct) {
        var provider = {
            supportsRequest: function (domainObject) {
                return domainObject.identifier.namespace === 'isf.taxonomy';
            },
            request: function (domainObject, options) {
                var points;
                return http.get('/server/log.json').then(function (result) {
                    return result.data[domainObject.identifier.key].filter(function (d) {
                        return d["timestamp"] > options.start && d["timestamp"] < options.end;
                    });
                });
            }
        };

        openmct.telemetry.addProvider(provider);
    }
}
