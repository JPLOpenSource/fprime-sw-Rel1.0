/* Used to deserialize incoming packets
// Size is in bytes
// In the format of:
// (4) Size of packet in bytes (Excluding the size of the size of packet information)
// (4) Descriptor
// (4) ID
// (2) Time base
// (1) Time context
// (4) Time in seconds
// (4) Microseconds
// (Size of packet - 19) Value
*/

// Dependencies
var telem = require('./../res/dictionary.json').isf;	// Get format dictionary

// Utils
var vsprintf = require("sprintf-js").vsprintf;

function numConverter(hexValue, type) {
	if (type.substring(0,1) === 'F') {
		var dv = new DataView(new ArrayBuffer(8));
		dv.setUint32(0, parseInt("0x" + hexValue));
		return dv.getFloat32(0);
	} else {
		return parseInt(hexValue, 16);
	}
}

function stringFormatter(hexValue, strBase, argTypes) {
	// In case of non number value:

	hexValue = hexValue.toString();	// Reinforce string type
	var args = [];	// Arg array

	// Pointer to keep track of values
	var ptr = 0;
	argTypes.forEach(function (type) {
		// Arg type used to decode each value
		var argToPush;
		if (typeof type === "string") {
			// Non Enum type
			if (type === "String") {
				// If string type

				// Get limit for pointer
				var charLimit = (2 * parseInt(hexValue.substring(ptr, ptr += 4), 16)) + ptr;

				// Create string through conversion of hex to char
				argToPush = "";
				while (ptr < charLimit) {
					argToPush += String.fromCharCode(parseInt(hexValue.substring(ptr, ptr += 2), 16));
				}
			} else {
				// Number type
				var numType = type.substring(0,1);
				var bits = parseInt(type.substring(1), 10);
				var rawNumStr = hexValue.substring(ptr, ptr += (bits / 4));
				if (numType === 'F') {
					argToPush = numConverter(rawNumStr);
				} else {
					argToPush = parseInt(rawNumStr, 16);
				}
			}
		} else {
			// Enum type
			var index = parseInt(hexValue.substring(ptr, ptr += 2), 16);
			argToPush = type[index.toString()];
		}
		args.push(argToPush);
	});

	// Sprintf with arg array as arguments
	return vsprintf(strBase, args);
}

// Get telem list for format lookup

// Size of packet besides the value and packet size (Descriptor, ID...Time USec) in nibbles
const packDescrSize = 38;

function deserialize(data) {
	var res = [];

	var packetLength = data.toString('hex').length;
	var ptr = 0;
	while (ptr < packetLength) {

		// Ptr is incremented in nibbles since each character is a hex representation
		var size         = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var descriptor   = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var	id           = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var timeBase     = parseInt(data.toString('hex').substring(ptr, ptr += 4), 16);
		var timeContext  = parseInt(data.toString('hex').substring(ptr, ptr += 2), 16);
		var timeSeconds  = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		var timeUSeconds = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);

		// Find telemetry format specifiers
		var telemData;
		if (descriptor === 1) {
			// If channel
			telemData = telem["channels"][id.toString()];
		} else if (descriptor === 2) {
			// If event
			telemData = telem["events"][id.toString()];
		}

		// Get size of value in nibbles
		var valueSize = (size * 2) - packDescrSize;
		// Get hexvalue
		var hexValue = data.toString('hex').substring(ptr, ptr += valueSize);

		var value;
		if (telemData) {
			// If found in dictionary
			switch(telemData["telem_type"]) {
				case "channel":
					// If channel type
					if (telemData["format_string"]) {
						value = vsprintf(telemData["format_string"], [numConverter(hexValue, telemData["type"])]);
					} else {
						value = numConverter(hexValue, telemData["type"]);
					}
					break;

				case "event":
					// If event type
					var strBase = telemData["format_string"];
					var argTypes = telemData["arguments"];
					value = stringFormatter(hexValue, strBase, argTypes);
					break;

				default:
					// None
					break;
			}
		} else {
			console.log("[ERROR] No matching found in format dictionary")
		}

		// Create timestamp by concatenating the microseconds value onto the seconds value.
		var timestamp = parseInt((timeSeconds.toString().concat(timeUSeconds.toString())).substring(0, 13), 10);

		var toMCT;
		// Create datum in openMCT format
		if (telemData["telem_type"] === 'event') {
			// Put event in channel id '-1'
			id = -1;
		}

		toMCT = {
			'timestamp':timestamp,
			'value':value,
			'name': telemData["name"],
			'identifier': id.toString(),
			'id': id.toString(),
			'type': telemData["telem_type"]
		};

		res.push(toMCT);

	}
	return res;
}

// Returns an array of channel ids
function getIds() {
	var ids = [];
	var channels = telem["channels"];
	for (var id in channels) {
		ids.push(id);
	}
	return ids;
}

// Export
module.exports = {
	deserialize: deserialize,
	getIds: getIds
};

