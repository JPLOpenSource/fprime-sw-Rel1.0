function getDictionary() {
    return http.get('./dictionary.json')
        .then(function (result) {
            return result.data;
        });
}

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
                var measurement = dictionary.measurements.filter(function (m) {
                    return m.key === identifier.key;
                })[0];

                // Object provider for each object in measurments. 
                // Does not populate tree
                return {
                    identifier: identifier,
                    name: measurement.name,
                    type: 'isf.telemetry',
                    telemetry: {
                        values: measurement.values  // Values already in default format
                    },
                    location: 'isf.taxonomy:isf'
                };
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
            return dictionary.measurements.map(function (m) {
                return {
                    // Return a list of dictionary objects with following values
                    // from each measurement
                    namespace: 'isf.taxonomy',
                    key: m.key
                };
            });
        });
    }
};

// Actual plugin. Must be a function with 'openmct' result operand and 
// must return function of 'install (openmct)'
var DictionaryPlugin = function (openmct) {
    // Return function of plugin
    return function install(openmct) {
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

        openmct.types.addType('isf.telemetry', {
            name: 'ISF Telemetry point',
            description: 'Telemetry point from ISF.',
            cssClass: 'icon-telemetry'  // Specify icon for type
        });
    };
};
