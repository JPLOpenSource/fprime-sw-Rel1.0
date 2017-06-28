// Historical telemetry plugin. Not live feed.

function HistoricalTelemetryPlugin() {
	return function install (openmct) {
		var provider = {
			// supportsRequest used to get telemetry from a telemetry store
			supportsRequest: function (domainObject) {
				// Place inside root/domainObject
				return domainObject.type === 'example.telemetry';
			},
			// Get data within options (start and end from options object attributes)
			request: function (domainObject, options) {
				var url = 'http://localhost:8081/telemetry/' +
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


