// Serializes command
var commandDict = require('./../res/dictionary.json').isf.commands;

function numSerBuff(num, bytes) {
  let intNum;
  let hexNum;
  if (typeof num == 'string') {
    // Presumed hex
    intNum = parseInt(num, 16);
    hexNum = num.split('x').pop();
  } else if (typeof num == 'number') {
    intNum = num;
    hexNum = num.toString(16);
  } else {
    // Not hex nor a string
    return num;
  }

  let zeroBuffAmount = (bytes * 2) - hexNum.length;
  if (bytes == 0) {
    zeroBuffAmount = 0;
  }

  let buffHex = '0'.repeat(zeroBuffAmount) + hexNum;

  let serialized = buffHex.match(/.{1,2}/g).map((h) => String.fromCharCode(parseInt(h, 16))).join('');
  console.log(serialized);

  return serialized;
}

function strSerBuff(str) {
  let length = numSerBuff(str.length, 2);
  let serializedString = length + str;
  return serializedString;
}

// function serString(str) {
//     let length = str.length;
//     let strBuff = str.split('').map((c) => c.charCodeAt(0))
// }

function serialize(command) {
  /*
  // Commands follow the following format\
  // header + (32-bit)(32-bit)Descriptor + 
  */
  const header = 'A5A5 FSW ZZZZ';
  const desc = 0;

  let argStartIndex = command.indexOf('(') + 1;
  let argEndIndex = command.indexOf(')');

  let commandName = command.substring(0, command.indexOf('('));
  let args = command.substring(argStartIndex, argEndIndex).split(',') // Create array with args after each comma
             .map((a) => a.trim())  // Remove whitespace
             .filter((a) => a != '');  // Remove empty strings

  let opcode;
  let packetArgs = '';
  let length = 8; // Length of packet in bytes starting with descriptor(4) and opcode(4).
  for (id in commandDict) {
    if (commandDict[id]['name'] === commandName) {
      opcode = parseInt(id);

      // Run Checks
      let cmd = commandDict[id];

      cmd['arguments'].forEach(function (a, i) {
        cmdType = a['type'];
        if (cmdType == 'String') {

        } else if (cmdType == 'Enum')  {

        } else {
          // Number type
          let argSize = parseInt(cmdType.substring(1)) / 8; // Size of argument in bytes
          length += argSize;
          packetArgs += numSerBuff(args[i], argSize);
        }
      });
    }
  }

  let commandPacket = header + numSerBuff(length, 4) + numSerBuff(desc, 4) + numSerBuff(opcode, 4) + packetArgs;

  console.log('command packet: ' + commandPacket, typeof commandPacket);
  return commandPacket;
}

// Export
module.exports = {
  serialize: serialize
};

// Tests
if (require.main === module) {
  let result = serialize('CMD_NO_OP()');
  console.log(result);
}
