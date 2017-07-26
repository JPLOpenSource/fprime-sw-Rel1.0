var hostSite = 'localhost';
var hostPort = '8080';
function getDictionary() {
    // Needs directory from root of application
    return http.get('/server/res/dictionary.json').then(function (result) {
        return result.data;
    });
}

// Value formatters
var value_format = {
    "hints": {
        "range": 1
    }, 
    "key": "value", 
    "max": 100, 
    "min": 0, 
    "name": "Value", 
    "units": "units"
};
var time_format = {
    "key": "utc",
    "source": "timestamp",
    "name": "Timestamp",
    "format": "utc",
    "hints": {
        "domain": 1
    }
};
var name_format = {
    "hints": {
        "range": 2
    },
    "key": "name",
    "name": "Name"
};
var id_format = {
    "hints": {
        "range": 3
    },
    "key": "identifier",
    "name": "ID"
};
var severity_format = {
    "hints": {
        "range": 4
    },
    "key": "severity",
    "name": "Severity"
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
                var measurement = dictionary.isf.channels[identifier.key];

                // Object provider for each object in measurments. 
                // Does not populate tree

                if (measurement.name === "Events") {
                    return {
                        identifier: identifier,
                        name: measurement.name,
                        type: 'isf.event',
                        telemetry: {
                            values: [
                                time_format, 
                                name_format, 
                                id_format, 
                                value_format, 
                                severity_format
                            ]  // Values already in default format
                        },
                        location: 'isf.taxonomy:isf'
                    };
                } else {
                    var typeStr = 'isf.' + measurement['id'].toString();
                    return {
                        identifier: identifier,
                        name: measurement.name,
                        type: 'isf.telemetry',
                        // type: typeStr,
                        telemetry: {
                            values: [
                                time_format,
                                name_format,
                                id_format,
                                value_format,
                            ]  // Values already in default format
                        },
                        location: 'isf.taxonomy:isf'
                    };
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
            var channels = [];
            var chanDict = dictionary["isf"]["channels"];
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
    hostSite = site;
    hostPort = port.toString();
    
    // Return function of plugin
    return function install(openmct) {
        // var chanDict;
        // getDictionary().then(function (dictionary) {
        //     chanDict = dictionary["isf"]["channels"];
        // });
        // Define what this plugin will do

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

        // Add types to events
        openmct.types.addType('isf.event', {
            name: 'ISF Event',
            description: 'Event from ISF',
            cssClass: 'icon-info'
        });

        // for (var id in chanDict) {
            // openmct.types.addType('isf.85', {
            //     name: chanDict["85"]["name"],
            //     description: chanDict["85"]["description"],
            //     cssClass: 'icon-telemetry'
            // });
        // }

        // console.log(openmct.types.listKeys());

        openmct.types.addType('isf.telemetry', {
            name: 'Isf Telemetry Point',
            description: 'Isf telemetry point from our happy tutorial.',
            cssClass: 'icon-telemetry'
        });
        
    };
};
