/**
  * deserialize-cosmos-binary.js
  *
  * Reads binary packets formatted for COSMOS logs
  *
  * author: Aaron Doubek-Kraft aaron.doubek-kraft@jpl.nasa.gov
  **/

const fs = require('fs');
const path = require('path');
const net = require('net');
const BSON = require('bson');

const deserialize = require('../src/util/deserialize-binary');
const config = require('../config.js');
const BSONAdapter = require('../src/bson-adapter');

const filename = process.argv[2];
const filepath = path.normalize(__dirname + '/' + filename);
const outFilepath = path.normalize(__dirname + '/../res/COSMOSLog.json');
const bson = new BSON();

if (!filename) {
    console.log('Usage: node deserialize-cosmos-binary.js <COSMOS Binary log file>');
    process.exit();
} else {
    console.log(`Reading COSMOS binary log from ${filepath}`)
}

// Format of binary header. Lengths specified in bytes.
const headerFormat = [
    {
        name: 'Marker',
        key: 'marker',
        type: 'S',
        length: 8
    },
    {
        name: 'Type',
        key: 'type',
        type: 'S',
        length: 4
    },
    {
        name: 'MD5',
        key: 'md5',
        type: 'S',
        length: 32
    },
    {
        name: 'Underscore',
        key: 'underscore',
        type: 'S',
        length: 1
    },
    {
        name: 'Hostname',
        key: 'hostname',
        type: 'S',
        length: 83
    }
]

// Packet definition. Strings in length field indicate that this property is
// variable length, and the length will be read from the named property of the packet.
// Lengths are specified in bytes
const packetFormat = [
    {
        name: 'Time Seconds',
        key: 'timeSeconds',
        type: 'I',
        length: 4
    },
    {
        name :'Time Microseconds',
        key: 'timeUSeconds',
        type: 'I',
        length: 4
    },
    {
        name: 'Target Name Length',
        key: 'targetNameLength',
        type: 'U',
        length: 1
    },
    {
        name: 'Target Name',
        key: 'targetName',
        type: 'S',
        length: 'targetNameLength'
    },
    {
        name: 'Packet Name Length',
        key: 'packetNameLength',
        type: 'U',
        length: 1
    },
    {
        name: 'Packet Name',
        key: 'packetName',
        type: 'S',
        length: 'packetNameLength'
    },
    {
        name: 'Packet Length',
        key: 'packetLength',
        type: 'U',
        length: 4
    },
    {
        name: 'Packet',
        key: 'packet',
        type: 'B',
        length: 'packetLength'
    }
];

//Read a packet of the given format
function readPacket(data, format, offset) {
    let packetOffset = 0,
        packet = {},
        length = format.length;

    for (let i = 0; i < length; i += 1) {
        let item = format[i],
            bitLen,
            byteLen;

        if (typeof item.length === 'number') {
            byteLen = item.length;
        } else if (typeof item.length === 'string') {
            byteLen = packet[item.length];
        } else {
            throw new Error(`Invalid length field in ${item.name}`)
        }

        bitLen = byteLen * 8;

        if (item.type === 'B') {
            let packetData = data.slice(offset, offset + byteLen);
            value = deserialize.deserialize(packetData, config.binaryInput.deployment);
            if (value && value[0]) {
                value = value[0]
            }
        } else {
            value = deserialize.readBuff(data, bitLen, item.type, offset);
        }

        packet[item.key] = value;
        offset += byteLen;
        packetOffset += byteLen;
    }

    return {
        packet: packet,
        offset: packetOffset
    }
}

let data = fs.readFileSync(filepath),
    totalOffset = 0,
    len = data.length,
    packets = []

let header = readPacket(data, headerFormat, totalOffset);
totalOffset += header.offset;

//read the metadata packet and ignore, not sure how to deserialize it correctly
let metapacket = readPacket(data, packetFormat, totalOffset);
totalOffset += metapacket.offset;

while (totalOffset < len) {
    let packetData = readPacket(data, packetFormat, totalOffset);
    totalOffset += packetData.offset;
    packets.push(packetData.packet.packet);
}

console.log(`Writing JSON log to ${outFilepath}`);
fs.writeFileSync(outFilepath, JSON.stringify(packets));

// abuse the BSONAdapter to send packets over a websocket with nice error handling
let adapter = new BSONAdapter(config);

let openMCTTelemetryClient = {
    socket: new net.Socket(),
    name: "OpenMCT BSON Stream Socket",
    port: config.input.port,
    site: config.input.bindAddress,
    successFunction: function () {
        console.log('Sending packets to BSON server...')
        packets.forEach( (packet) => {
            if (packet) {
                let packetAsBSON = bson.serialize(packet);
                this.socket.write(packetAsBSON);
            }
        });
        console.log('All packets sent, exiting')
        this.socket.end();
    }
};

adapter.connectSocket(openMCTTelemetryClient).catch( (reject) => {
    adapter.printRejectNotice(reject, openMCTTelemetryClient);
    adapter.handleConnectionError(reject, openMCTTelemetryClient);
});
