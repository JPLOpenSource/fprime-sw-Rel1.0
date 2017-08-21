// Serializes command
var commandDict = require('./../res/dictionary.json').isf.commands;

function numBuff(num, bits, type) {
  let buff = Buffer.alloc(bits / 8);
  switch (type) {
    case 'U': {
      // Unsigned Int
      switch(bits) {
        case 8: {
          buff.writeUInt8(num);
          break;
        }
        case 16: {
          buff.writeUInt16BE(num);
          break;
        }
        case 32: {
          buff.writeUInt32BE(num);
          break;
        }
        default: {
          // Invalid bits
          break;
        }
      }

      break;
    }

    case 'F': {
      // Floating Point
      switch(bits) {
        case 32: {
          buff.writeFloatBE(num);
          break;
        }
        default: {
          // Invalid bits
          break;
        }
      }

      break;
    }

    case 'I': {
      // Integer
      switch(bits) {
        case 8: {
          buff.writeInt8BE(num);
          break;
        }
        case 16: {
          buff.writeInt16BE(num);
          break;
        }
        case 32: {
          buff.writeInt32BE(num);
          break;
        }
        default: {
          // Invalid bits
          break;
        }
      }

      break;
    }

    case 'D': {
      // Double
      switch(bits) {
        case 64: {
          buff.writeDoubleBE(num);
          break;
        }

        default: {
          // Invalid bits
          break;
        }
      }

      break;
    }

    default: {
      // Invalid type
      break;
    }
  }

  return buff;
}



function concatBuffs(buffArr) {
  let totalLength = buffArr.reduce((total, b) => total + b.length, 0);
  return Buffer.concat(buffArr, totalLength);
}

function strBuff(str) {
  let lenBuff = numBuff(str.length, 16, 'U');
  let strBuff = Buffer.from(str);
  return concatBuffs([lenBuff, strBuff]);
  
}

function serialize(usrCommand) {
  /*
  // Commands follow the following format\
  // header + (32-bit)(32-bit)Descriptor + 
  */
  const header = 'A5A5 FSW ZZZZ';
  const desc = 0;

  let length = 8; // Length in bytes
  let opcode = usrCommand['id'];
  let types = commandDict[opcode.toString()]['arguments'].map((a) => a['type']);

  let argBufferArr = usrCommand['arguments'].map(function (a, i) {
    if (types[i] != 'String') {
      let bits = parseInt(types[i].substring(1));
      length += (bits / 8);
      return numBuff(a, bits, types[i]);
    } else {
      let stringBuffed = strBuff(a);
      length += stringBuffed.length;
      return stringBuffed;
    }
  });

  let commandBufferArgs = concatBuffs(argBufferArr);

  console.log('opcode: ', opcode + '\n');

  let commandBuffArray = [Buffer.from(header), numBuff(length, 32, 'U'), numBuff(desc, 32, 'U'), numBuff(opcode, 32, 'U'), commandBufferArgs];
  

  return concatBuffs(commandBuffArray);
  // return Buffer.from(example);
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
