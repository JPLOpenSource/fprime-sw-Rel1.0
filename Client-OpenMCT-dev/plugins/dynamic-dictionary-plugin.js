// Plugin for OpenMCT's dictionary

// Create websocket
var site = 'localhost';
var port = 1337;


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

        // Turn root into ISF folder
        openmct.objects.addProvider('isf.taxonomy', {
            get: function (identifier) {
                return Promise.resolve({
                    identifier: identifier,
                    name: 'ISF',
                    type: 'folder',
                    location: 'ROOT'
                });
            }
        });

        openmct.objects.addProvider('isf.channels', {
            get: function (identifier) {
                return Promise.resolve({
                    identifier: identifier,
                    name: 'Channels',
                    type: 'folder',
                    location: 'isf.taxonomy:channels'
                });
            }
        });

        openmct.objects.addProvider('isf.events', {
            get: function (identifier) {
                return Promise.resolve({
                    identifier: identifier,
                    name: 'Events',
                    type: 'folder',
                    location: 'isf.taxonomy:events'
                });
            }
        });

        var folders = [
            {
                namespace: 'isf.channels',
                key: 'channels'
            },
            {
                namespace: 'isf.events',
                key: 'events'
            }
        ];

        openmct.composition.addProvider({
            appliesTo: function (domainObject) {
                return domainObject.identifier.namespace === 'isf.taxonomy';
            },
            load: function (domainObject) {
                return Promise.resolve(folders);
            }
        });

        openmct.types.addType('isf.telemetry', {
            name: 'ISF Telemetry point',
            description: 'Telemetry point from ISF.',
            cssClass: 'icon-telemetry'  // Specify icon for type
        });
    };
};