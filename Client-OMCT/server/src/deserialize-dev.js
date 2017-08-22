// Dependencies
var telem = require('./../res/dictionary.json').isf;  // Get format dictionary

// Utils
var vsprintf = require('sprintf-js').vsprintf;

function readBuff(buff, bits, type, offset) {
  if (typeof offset == "undefined") {
      offset = 0;
  }
  switch(type.substring(0,1)) {
    case 'U': {
      switch(bits) {
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
          console.log("[ERROR] Invalid UInt size!");
          return null;
        }
      }
    }

    case 'I': {
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
      console.log("[ERROR] Invalid type!");
      return null;
    }
  }
}

function stringFormatter(buff, strBase, argTypes) {
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
        let bits = parseInt(type.substring(0, 1), 10);
        let num = readBuff(buff, bits, type, offset);
        offset += bits / 8;

        return num;
      }
    } else {
      // Enum type
      let index = readBuff(buff, 8, 'I', offset);
      return type[index.toString()];
    }
  });

  return vsprintf(strBase, args); 
}

function gainOffsetConv(value, gain, offset) {
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

function deserialize(data) {
  let packetArr = [];
  let packetLength = data.length;

  let offset = 0;
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
      console.log("[ERROR] Invalid descriptor");
      return null;
    }

    let valueLen = size - packetDescriptionLen;
    let valueBuff = data.slice(offset, offset += valueLen);

    // If found in dictionary
    let value;
    switch(telemData['telem_type']) {
      case 'channel': {
        // If channel type
        let type = telemData['type'].substring(0,1);
        let bits = parseInt(telemData['type'].substring(1), 10);
        if (telemData['format_string']) {
          value = vsprintf(telemData['format_string'], [ readBuff(valueBuff, bits, type, offset) ]);
        } else {
          value = readBuff(valueBuff, bits, type, offset);
        }
        break;
      }

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

    // Create datums for eac unit type
    let units = telemData['units'];
    if (units != null) {
      units.forEach(function (u) {
        let keyForm = 'value:' + u['Label'];
        let valueForm = gainOffsetConv(value, parseInt(u['Gain'], 10), parseInt(u['Offset'], 10));
        toMCT[keyForm] = valueForm;
      });
    }

    // Push packet into queue
    packetArr.push(toMCT);

  }

  return packetArr;
}