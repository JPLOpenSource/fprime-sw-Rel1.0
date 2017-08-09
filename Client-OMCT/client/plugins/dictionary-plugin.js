// Value formatters
const value_format = {
	'hints': {
		'range': 2
	}, 
	'key': 'value', 
	'max': 100, 
	'min': 0, 
	'name': 'Value', 
	'units': 'units'
};
const time_format = {
	'key': 'utc',
	'source': 'timestamp',
	'name': 'Timestamp',
	'format': 'utc',
	'hints': {
		'domain': 1
	}
};
const name_format = {
	'hints': {
		'domain': 2
	},
	'key': 'name',
	'name': 'Name'
};
const id_format = {
	'hints': {
		'domain': 3
	},
	'key': 'identifier',
	'name': 'ID'
};
const severity_format = {
	'hints': {
		'range': 1
	},
	'key': 'severity',
	'name': 'Severity'
};

var objectProvider = {
	get: function (identifier) {
		// Return promise of function
		// Get json dictionary
		return getDictionary().then(function (dictionary) {
			// Create and describe domain object from root
			// Indentifier contians key and namespace
			if (identifier.key === 'isf') {
				return {
					// Provider if isf root
					identifier: identifier, // Domain object 'identifier' is same as root
					name: 'ISF',  // Name of toplevel dictionary object ('ISF')
					type: 'folder', 
					location: 'ROOT'
				};
			} else {
				// Provider if not isf root
				

				// Measurement = measurement object with same key as 'identifier.key'
				let measurement = dictionary.isf.channels[identifier.key];


				value_formats = [name_format, id_format, time_format, value_format];
				let units = measurement['units'];
				if (units != null) {
					units.forEach(function (u, i) {
						let value_format_save = Object.assign({}, value_format);
						value_format_save['units'] = u['Label'];
						value_format_save['key'] = 'value:' + u['Label'];
						value_format_save['hints']['range'] = i + 2;
						value_format_save['name'] = u['Label'];
						value_formats.push(value_format_save);
					});
				}

				// Object provider for each object in measurments. 
				// Does not populate tree

				let typeStr = 'isf.telemetry';
				// console.log('type' + typeStr);

        let toReturn = {
          identifier: identifier,
          name: measurement.name,
          type: typeStr,
          notes: measurement['description'],
          // type: typeStr,
          telemetry: {
            values: value_formats  // Values already in default format
          },
          location: 'isf.taxonomy:isf'
        }
				if (measurement.name === 'Events') {
					// Object provider for events
					toReturn.telemetry.values.push(severity_format);
					toReturn.telemetry.values.forEach(function (v, i) {
						v['hints'] = {
							'range': i + 1
						}
					});
					return toReturn;
				} else {
					// Object provider for all channels
					toReturn.limits = measurement['limits'];
					return toReturn;
				}
			}
		});
	}
};

var compositionProvider = {
	appliesTo: function (domainObject) {
		// Determines what object this composition provider will provide
		// In this case, the isf.taxonomy domain object with a type of folder.
		return domainObject.identifier.namespace === 'isf.taxonomy' &&
			   domainObject.type === 'folder';
	},
	load: function (domainObject) {
		// Returns promise of an array of domain objects, in this case list of measurements.
		return getDictionary().then(function (dictionary) {
			// 'dictionary.measurements' is a list of telemetry objects
			let channels = [];
			let chanDict = dictionary['isf']['channels'];
			for (id in chanDict) {
				channels.push({
					namespace: 'isf.taxonomy',
					key: id
				});
			}

			return channels;
		});
	}
};

// Actual plugin. Must be a function with 'openmct' result operand and 
// must return function of 'install (openmct)'
function DictionaryPlugin(site, port) {
	// Return function of plugin
	return function install(openmct) {
		// Create root of dictionary
		openmct.objects.addRoot({
			// Create identifier

			// Namespace used to identify which root 
			// to provide telemetry objects for
			namespace: 'isf.taxonomy',  
			key: 'isf'
		});

		// Create domain object ('isf' folder) under the root namespace 'isf.taxonomy'
		openmct.objects.addProvider('isf.taxonomy', objectProvider);

		// Composition provider will define structure of the tree and populate it.
		openmct.composition.addProvider(compositionProvider);

		openmct.types.addType('isf.telemetry', {
			name: 'Isf Telemetry Point',
			description: 'Isf telemetry point from Ref App.',
			cssClass: 'icon-telemetry'
		});
	};
};
