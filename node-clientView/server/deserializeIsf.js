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
var sprintf = require("sprintf-js").sprintf,
    vsprintf = require("sprintf-js").vsprintf

function floatConverter(hexValue) {
	var dv = new DataView(new ArrayBuffer(8));
	dv.setUint32(0, parseInt("0x" + hexValue));

	return dv.getFloat32(0);
}

function convertToString(hexValue, strBase, argTypes) {
	hexValue = hexValue.toString();	// Reinforce string type
	console.log(hexValue);
	var args = [];	// Arg array

	// Pointer to keep track of values
	var ptr = 0;
	argTypes.forEach(function (type) {
		var argToPush;
		if (Array.isArray(type) === false) {
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
				console.log(numType, bits);
				if (numType === 'F') {
					argToPush = floatConverter(rawNumStr);
				} else {
					argToPush = parseInt(rawNumStr, 16);
				}
			}
		} else {
			// Enum type
			var index = parseInt(hexValue.substring(ptr, ptr += 2), 16);
			argToPush = type[index];
		}
		args.push(argToPush);
	});
	console.log(args);
	return vsprintf(strBase, args);
}

// Get telem list for format lookup
var dict = require('../client/isf-omct/res/dictionary.json');
var telem = dict.measurements;
const packDescrSize = 38;	// Size of packet besides the value and packet size (Descriptor, ID...Time USex) in nibbles

function deserialize(data, numFormat) {
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

		

		var telemData;
		if (descriptor === 1) {
			// If channel
			telemData = telem.find(function (data) {
				return data["key"] == id && !("arg_format" in data);
			});
		} else if (descriptor === 2) {
			// If event
			telemData = telem.find(function (data) {
				return data["key"] == id && ("arg_format" in data);
			});
		}

		// Get size of value in nibbles
		var valueSize = (size * 2) - packDescrSize;
		// Get hexvalue
		var hexValue = data.toString('hex').substring(ptr, ptr += valueSize);

		var value;
		if (telemData) {
			var numFormat = telemData["num_type"];
			if (numFormat.indexOf("F") != -1) {
				// Convert to float
				value = floatConverter(hexValue);
			} else if (numFormat === "string") {
				// Convert to string
				var strBase = telemData["str_format"];
				var argTypes = telemData["arg_format"];
				value = convertToString(hexValue, strBase, argTypes);
				console.log(value);
			} else {
				// Get value from packet if no conversion is needed
				value = parseInt(hexValue, 16);
			}
		}

		// Create timestamp by concatenating the microseconds value onto the seconds value.
		var timestamp = parseInt((timeSeconds.toString()).concat(timeUSeconds.toString()), 10);

		// Create datum in openMCT format
		var toMCT = {
			'timestamp':timestamp,
			'value':value,
			'id':id.toString()
		};

		// console.log(toMCT, ptr, packetLength);
		res.push(toMCT);

	}
	return res;
}

// Export
module.exports = {
	deserialize: deserialize
};

