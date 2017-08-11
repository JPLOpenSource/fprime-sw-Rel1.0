// Serializes command

function serialize(command) {
    let argStartIndex = command.indexOf('(') + 1;
    let argEndIndex = command.indexOf(')');

    let commandName = command.substring(0, command.indexOf('('));
    let args = command.substring(argStartIndex, argEndIndex).split(',').map((a) => a.trim());

    // Turn to binary
    console.log(commandName, args);
}

// Export
module.exports = {
    serialize: serialize
};