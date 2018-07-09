/* deserialize-binary.js
 *
 * Util library for converting fprime binary packets to json
 *
 * Authors : Sanchit Sinha sinhasaeng@gmail.com
 *           Aaron Doubek-Kraft aarondou@jpl.nasa.gov
 */

// Utils
var vsprintf = require('sprintf-js').vsprintf;
var Long = require('long')

const typeCodes = {
    I: 71,
    U: 72,
    F: 73,
    S: 74,
    E: 74
}

const flags = {
    redHigh: 0x00100000,
    yellowHigh: 0x00040000,
    yellowLow: 0x00020000,
    redLow: 0x00080000,
    allGood: 0x00010000
}

/*
 * This function reads a buffer using the specified parameters
 * @param: {Buffer} buff - Node Buffer to read from
 * @param: {number} bits - Number of bits to read
 * @param: {string} type - 'U'nsigned, 'I'nteger, or 'F'loat
 * @param: {number} offset - Byte to start reading from
 * @returns: {number} - Number read
*/
function readBuff (buff, bits, type, offset) {
    if (typeof offset == "undefined") {
        offset = 0;
    }
    switch(type.substring(0,1)) {
        case 'U': {
            // Unsigned Int
            switch(bits) {
                case 64: {
                    let low = buff.readUInt32BE(offset),
                        high = buff.readUInt32BE(offset + 4),
                        longVal = new Long(high, low);
                    return longVal.toNumber();
                }
                case 32: {
                    return buff.readUInt32BE(offset);
                }
                case 16: {
                    return buff.readUInt16BE(offset);
                }
                case 8: {
                    return buff.readUInt8(offset);
                }
                default: {
                    // Invalid bit size
                    console.log("[ERROR] Invalid UInt size!: " + bits);
                    return null;
                }
            }
        }

        case 'I': {
            // Int
            switch(bits) {
                case 32: {
                    return buff.readInt32BE(offset);
                }
                case 16: {
                    return buff.readInt16BE(offset);
                }
                case 8: {
                    return buff.readInt8(offset);
                }
                default: {
                    // Invalid bit size
                    console.log("[ERROR] Invalid Int size!");
                    return null;
                }
            }
        }

        case 'F': {
            // Float
            switch(bits) {
                case 32: {
                    return buff.readFloatBE(offset);
                }
                default: {
                    // Invalid bit size
                    console.log("[ERROR] Invalid Float size!");
                    return null;
                }
            }
        }

        default: {
            // Invalid type
            console.log("[ERROR] Invalid type! " + type);
            return null;
        }
    }
}

function stringFormatter (buff, strBase, argTypes) {
    let offset = 0;
    let args = argTypes.map(function (type) {
        if (typeof type === 'string') {
            // Non-enum type
            if (type === 'String') {
                // String type
                const stringLengthLen = 2;
                let stringLength = readBuff(buff, stringLengthLen * 8, 'U', offset);
                offset += stringLengthLen;

                return buff.slice(offset, offset += stringLength).toString();
            } else {

                let bits = parseInt(type.substring(1), 10);
                let num = readBuff(buff, bits, type, offset);
                offset += bits / 8;
                return num;
            }
        } else if (typeof type === 'object') {
            // Enum type
            let index = readBuff(buff, 32, 'I', offset);
            return type[index.toString()];
        } else {
            // Invalid type
            console.log('[ERROR] Invalid argument type in string formatter!: ' + type);
        }
    });

    return vsprintf(strBase, args);
}

function gainOffsetConv (value, gain, offset) {
    return gain * value + offset;
}

// Packet sizes in bytes
const sizeLen = 4;
const descriptorLen = 4;
const idLen = 4;
const timeBaseLen = 2;
const timeContextLen = 1;
const secondsLen = 4;
const uSecLen = 4;
// Size of all packet descriptions except size. Used to calculate size of value
const packetDescriptionLen = 19;

/*
 * Deserialize a Fprime packet
 * @param {Buffer} - Input buffer array of raw packet
 * @target {string} - Target name (or deployment)
 * @return: Array of OpenMCT formatted dataum
 */
function deserialize (data, target) {
    var telem = require('./../../res/dictionary.json')[target.toLowerCase()];  // Get format dictionary

    let packetArr = [];
    let packetLength = data.length;
    let offset = 0;
    // Interact deserialized packets
    while (offset < packetLength) {
        let size = readBuff(data, sizeLen * 8, 'U', offset);
        offset += sizeLen;

        let descriptor = readBuff(data, descriptorLen * 8, 'U', offset);
        offset += descriptorLen;

        let id = readBuff(data, idLen * 8, 'U', offset);
        offset += idLen;

        let timeBase = readBuff(data, timeBaseLen * 8, 'U', offset);
        offset += timeBaseLen;

        let timeContext = readBuff(data, timeContextLen * 8, 'U', offset);
        offset += timeContextLen;

        let seconds = readBuff(data, secondsLen * 8, 'U', offset);
        offset += secondsLen;

        let uSec = readBuff(data, uSecLen * 8, 'U', offset);
        offset += uSecLen;

        // Find telemetry format specifiers
        let telemData;
        if (descriptor == 1) {
            // If channel
            telemData = telem['channels'][id.toString()];
        } else if (descriptor == 2) {
            // If event
            telemData = telem['events'][id.toString()];
        } else {
            console.log("[ERROR] Invalid descriptor: " + descriptor);
            return null;
        }

        let valueLen = size - packetDescriptionLen;
        let valueBuff = data.slice(offset, offset += valueLen);

        // If found in dictionary
        let value;
        switch(telemData['telem_type']) {
            case 'channel': {
                // If channel type
                let type = telemData['type'];
                let bits = parseInt(telemData['type'].substring(1), 10);
                if (telemData['format_string']) {
                    let modifierArg;
                    if (type === 'Enum') {
                        let index = readBuff(valueBuff, 32, 'I', 0);
                        modifierArg = telemData["enum_dict"][index.toString()];
                    } else {
                        modifierArg = readBuff(valueBuff, bits, type, 0);
                    }
                    value = vsprintf(telemData['format_string'], [modifierArg]);
                } else {
                    value = readBuff(valueBuff, bits, type, 0);
                }
                break;
            }
            case 'event':
                // If event typeß
                let strBase = telemData['format_string'];
                let argTypes = telemData['arguments'];
                // console.log(valueBuff, strBase, argTypes);
                value = stringFormatter(valueBuff, strBase, argTypes);
                break;

            default:
                // None
                break;
            }

            let timestamp = seconds * 1000 + uSec/1000.;

            let datum = {
                'timestamp': new Date(timestamp),
                'identifier': id.toString(),
                'flags': evaluateLimits(value, telemData.limits)
            };

            // Create datum in openMCT format
            if (telemData.telem_type === 'channel') {
                datum.name = telemData.name;
                datum.raw_type = getBSONTypeCode(telemData.type);
                datum.raw_value = value;
            } else if (telemData.telem_type === 'event') {
                datum.name = 'Events';
                datum.raw_type = getBSONTypeCode('S');
                datum.raw_value = telemData.name + ': ' + value;
            }

            // Create datums for eac unit type
            let units = telemData['units'];
            if (units != null) {
                units.forEach(function (u) {
                    let keyForm = 'value:' + u['Label'];
                    let valueForm = gainOffsetConv(value, parseInt(u['Gain'], 10), parseInt(u['Offset'], 10));
                    datum[keyForm] = valueForm;
                });
            }
            packetArr.push(datum);
        }
    return packetArr;
}

// Returns an array of channel ids
function getIds (target) {
    var telem = require('./../res/dictionary.json')[target.toLowerCase()];  // Get format dictionary
    let ids = [];
    let channels = telem['channels'];
    for (let id in channels) {
        ids.push(id);
    }
    return ids;
}

function evaluateLimits (value, limits) {
    let flag = flags.allGood;
    if (limits) {
        if (value > limits.high_red && limits.high_red !== null) {
            flag = flags.redHigh;
        } else if (value > limits.high_yellow && limits.high_yellow !== null) {
            flag = flags.yellowHigh;
        } else if (value < limits.low_red && limits.low_red !== null) {
            flag = flags.redLow;
        } else if (value < limits.low_yellow && limits.low_yellow !== null) {
            flag = flags.yellowLow;
        }
    }
    return flag;
}

function getBSONTypeCode (data_type) {
    var typeCode = data_type.charAt(0);
    return typeCodes[typeCode];
}

module.exports = {
    deserialize: deserialize,
    getIds: getIds
};
