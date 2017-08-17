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

function serialize(usrCommand) {
  /*
  // Commands follow the following format\
  // header + (32-bit)(32-bit)Descriptor + 
  */
  const header = 'A5A5 FSW ZZZZ';
  const desc = 0;

  let length = 8;
  let opcode = usrCommand['id'];
  let types = commandDict[opcode.toString()]['arguments'].map((a) => a['type']);

  let packetArgs = usrCommand['arguments'].map(function (a, i) {
    if (types[i] != 'String') {
      let bytes = parseInt(types[i].substring(1)) / 8;
      return numSerBuff(a, bytes);
    } else {
      return strSerBuff(a);
    }
  }).join('');

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
