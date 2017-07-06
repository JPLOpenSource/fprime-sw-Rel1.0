// Used to deserialize incoming packets

// Get dict
var dict = require('../client/isf-omct/res/dictionary.json');

function deserialize(data, numFormat) {
	var res = [];

	var packetLength = data.toString('hex').length;
	var ptr = 0;
	// while (ptr < packetLength) {

		var size         = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var descriptor   = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var	id           = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var timeBase     = parseInt(data.toString('hex').substring(ptr, ptr += 4), 16);
		var timeContext  = parseInt(data.toString('hex').substring(ptr, ptr += 2), 16);
		var timeSeconds  = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var timeUSeconds = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);

		var telem = dict.measurements;	// List of telemetry dictionary data
		var telemSize = dict.measurement_size;
		if (!(id in numFormat)) {
			console.log("New id: " + id);
			// If not saved in numFormat dictionary, find format for id
			var telem = dict.measurements;	// List of telemetry dictionary data
			var telemSize = dict.measurement_size;
			for (i = 0; i < telemSize; i++) {
				if (id.toString() === telem[i].key) {
					numFormat[id] = telem[i].num_type;
				}
			}
		}

		var valueSize = (size + 4) * 2 - ptr;
		// Check if floating point conversion is needed
		if (numFormat[id].indexOf("F") != -1) {
			var hexValue = data.toString('hex').substring(ptr, ptr += valueSize);	// Get value

			// Convert to float
			var dv = new DataView(new ArrayBuffer(8));
			dv.setUint32(0, parseInt("0x" + hexValue));
			var value = dv.getFloat32(0);
		} else {
			// Get value from packet if no conversion is needed
			var value = parseInt(data.toString('hex').substring(ptr, ptr += valueSize), 16);
		}

		var timestamp = parseInt((timeSeconds.toString()).concat(timeUSeconds.toString()), 10);

		// Create datum in openMCT format
		var toMCT = {
			'timestamp':timestamp,
			'value':value,
			'id':id.toString()
		};

		// console.log(toMCT, ptr, packetLength);
		res.push(toMCT);
		
	// }

	return res;
}

// Export
module.exports = {
	deserialize: deserialize
};

