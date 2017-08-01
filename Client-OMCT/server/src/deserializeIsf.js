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
var vsprintf = require('sprintf-js').vsprintf;

function numConverter(hexValue, type) {
	if (type.substring(0,1) === 'F') {
		let dv = new DataView(new ArrayBuffer(8));
		dv.setUint32(0, parseInt('0x' + hexValue));
		return dv.getFloat32(0);
	} else {
		return parseInt(hexValue, 16);
	}
}

function stringFormatter(hexValue, strBase, argTypes) {
	// In case of non number value:

	hexValue = hexValue.toString();	// Reinforce string type
	let args = [];	// Arg array

	// Pointer to keep track of values
	let ptr = 0;
	argTypes.forEach(function (type) {
		// Arg type used to decode each value
		let argToPush;
		if (typeof type === 'string') {
			// Non Enum type
			if (type === 'String') {
				// If string type

				// Get limit for pointer
				let charLimit = (2 * parseInt(hexValue.substring(ptr, ptr += 4), 16)) + ptr;

				// Create string through conversion of hex to char
				argToPush = '';
				while (ptr < charLimit) {
					argToPush += String.fromCharCode(parseInt(hexValue.substring(ptr, ptr += 2), 16));
				}
			} else {
				// Number type
				let numType = type.substring(0,1);
				let bits = parseInt(type.substring(1), 10);
				let rawNumStr = hexValue.substring(ptr, ptr += (bits / 4));
				if (numType === 'F') {
					argToPush = numConverter(rawNumStr);
				} else {
					argToPush = parseInt(rawNumStr, 16);
				}
			}
		} else {
			// Enum type
			let index = parseInt(hexValue.substring(ptr, ptr += 2), 16);
			argToPush = type[index.toString()];
		}
		args.push(argToPush);
	});

	// Sprintf with arg array as arguments
	return vsprintf(strBase, args);
}

function gainOffsetConv(value, gain, offset) {
	return value * gain + offset;
}
// Get telem list for format lookup

// Size of packet besides the value and packet size (Descriptor, ID...Time USec) in nibbles
const packDescrSize = 38;

function deserialize(data) {
	let res = [];

	let packetLength = data.toString('hex').length;
	let ptr = 0;
	while (ptr < packetLength) {

		// Ptr is incremented in nibbles since each character is a hex representation
		let size         = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		let descriptor   = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		let	id           = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		let timeBase     = parseInt(data.toString('hex').substring(ptr, ptr += 4), 16);
		let timeContext  = parseInt(data.toString('hex').substring(ptr, ptr += 2), 16);
		let timeSeconds  = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);
		let timeUSeconds = parseInt(data.toString('hex').substring(ptr, ptr += 8), 16);

		// Find telemetry format specifiers
		let telemData;
		if (descriptor === 1) {
			// If channel
			telemData = telem['channels'][id.toString()];
		} else if (descriptor === 2) {
			// If event
			telemData = telem['events'][id.toString()];
		}

		// Get size of value in nibbles
		let valueSize = (size * 2) - packDescrSize;
		// Get hexvalue
		let hexValue = data.toString('hex').substring(ptr, ptr += valueSize);

		let value;
		if (telemData) {
			// If found in dictionary
			switch(telemData['telem_type']) {
				case 'channel':
					// If channel type
					if (telemData['format_string']) {
						value = vsprintf(telemData['format_string'], [numConverter(hexValue, telemData['type'])]);
					} else {
						value = numConverter(hexValue, telemData['type']);
					}
					break;

				case 'event':
					// If event type
					let strBase = telemData['format_string'];
					let argTypes = telemData['arguments'];
					value = stringFormatter(hexValue, strBase, argTypes);
					break;

				default:
					// None
					break;
			}
		} else {
			console.log('[ERROR] No matching found in format dictionary')
		}

		// Create timestamp by concatenating the microseconds value onto the seconds value.
		let timestamp = parseInt((timeSeconds.toString().concat(timeUSeconds.toString())).substring(0, 13), 10);

		let toMCT = {
			'timestamp':timestamp,
			'value':value,
			'name': telemData['name'],
			'identifier': id.toString(),
			'id': id.toString(),
			'type': telemData['telem_type']
		};

		// Create datum in openMCT format
		if (telemData['telem_type'] === 'event') {
			// Put event in channel id '-1'
			toMCT['id'] = '-1';
			// Add severity
			toMCT['severity'] = telemData['severity'];
		}

		let units = telemData['units'];
		if (units != null) {
			units.forEach(function (u) {
				let keyForm = 'value:' + u['Label'];
				let valueForm = gainOffsetConv(value, parseInt(u['Gain'], 10), parseInt(u['Offset'], 10));
				toMCT[keyForm] = valueForm;
			});
		}

		res.push(toMCT);

	}
	return res;
}

// Returns an array of channel ids
function getIds() {
	let ids = [];
	let channels = telem['channels'];
	for (let id in channels) {
		ids.push(id);
	}
	return ids;
}

// Export
module.exports = {
	deserialize: deserialize,
	getIds: getIds
};

