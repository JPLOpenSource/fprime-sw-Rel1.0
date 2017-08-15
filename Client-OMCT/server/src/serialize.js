// Serializes command
var commandDict = require('./../res/dictionary.json').isf.commands;

function serBuff(num, bytes) {
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
    return NaN;
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

// function serString(str) {
//     let length = str.length;
//     let strBuff = str.split('').map((c) => c.charCodeAt(0))
// }

function serialize(command) {
  let argStartIndex = command.indexOf('(') + 1;
  let argEndIndex = command.indexOf(')');

  let commandName = command.substring(0, command.indexOf('('));
  let args = command.substring(argStartIndex, argEndIndex).split(',').map((a) => a.trim());

  const header = 'A5A5 FSW ZZZZ';
  const desc = 0;

  let opcode;
  let packetArgs = '';
  let length = 8; // Length of packet in bytes starting with descriptor(4) and opcode(4).
  for (id in commandDict) {
    if (commandDict[id]['name'] === commandName) {
      opcode = parseInt(id);

      // Run Checks
      let cmd = commandDict[id];
      if (cmd['arguments'].length != args.length) {
        // return null;
      }

      cmd['arguments'].forEach(function (a, i) {
        let argSize = parseInt(a['type'].substring(1)) / 8; // Size of argument in bytes
        length += argSize;
        packetArgs += serBuff(args[i], argSize);
      });
    }
  }

  let commandPacket = header + serBuff(len, 4) + serBuff(desc, 4) + serBuff(opcode, 4) + packetArgs;

  console.log('command packet: ' + commandPacket, typeof commandPacket);
  return commandPacket;
}

// Export
module.exports = {
  serialize: serialize
};