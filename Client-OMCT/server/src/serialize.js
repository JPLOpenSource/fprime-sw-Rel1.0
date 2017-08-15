// Serializes command
var commandDict = require('./../res/dictionary.json').isf.commands;

function buff(int, bytes) {
    let hexVal = int.toString(16);
    return '0'.repeat(repeatAmount) + hexVal;
}

function serialize(command) {
    let argStartIndex = command.indexOf('(') + 1;
    let argEndIndex = command.indexOf(')');

    let commandName = command.substring(0, command.indexOf('('));
    let args = command.substring(argStartIndex, argEndIndex).split(',').map((a) => a.trim());

    const header = "A5A5 FSW ".split('').map((char) => char.charCodeAt(0)).join('');
    const desc = "0000";

    let opcode;
    for (id in commandDict) {
        if (commandDict[id]['name'] === commandName) {
            opcode = parseInt(id);
        }
    }

    let length = 8;

    let data = header + '0008' + '0000' + opcode

    console.log(data);

    let commandPacket = new Buffer.from(JSON.stringify({
        'type': 'Buffer',
        'data': data.split('').map((num) => parseInt(num))
    }));



    return commandPacket;
}

// Export
module.exports = {
    serialize: serialize
};