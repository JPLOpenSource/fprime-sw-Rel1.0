/*
    generateJSON.js

    Given a JSON dictionary for an fprime app, generate JSON configuration
    files for the openmct bson server. Points file is saved in "points.json",
    packets file is saved in "packets.json"

    Author: Aaron Doubek-Kraft aaron.doubek-kraft@jpl.nasa.gov

*/

const fs = require('fs');
const path = require('path');

const dictJSON = fs.readFileSync(path.dirname(__dirname) + '/server/res/dictionary.json', {encoding: 'UTF-8'}),
      outFilenamePoints = 'openmct-telemetry-server/points.json',
      outFilenamePackets = 'openmct-telemetry-server/packets.json',
      dict = JSON.parse(dictJSON),
      ref = dict.ref,
      pointDict = {}
      packetDict = {
          "Channels": {
              name: "Channels",
              points: []
          }
      };

let value_format = {
  'hints': {
    'range': 2
  },
  'key': 'value',
  'max': 100,
  'min': 0,
  'name': 'Value',
  'units': 'units'
};
let time_format = {
  'key': 'utc',
  'source': 'timestamp',
  'name': 'Timestamp',
  'format': 'utc',
  'hints': {
    'domain': 1
  }
};
let name_format = {
  'hints': {
    'domain': 2
  },
  'key': 'name',
  'name': 'Name'
};
let id_format = {
  'hints': {
    'domain': 3
  },
  'key': 'identifier',
  'name': 'ID'
};
let raw_value_format = {
    key: "raw_value",
    name: "Raw Value",
    hints: {"range":2}
};

Object.entries(ref.channels).forEach(function (channel) {
    let id = channel[0],
        props = channel[1],
        name = props.name;

    packetDict['Channels'].points.push(name);
    pointDict[name] = {
        name: name,
        key: name,
        id: name,
        values: [time_format, name_format, id_format, raw_value_format]
    }
});

fs.writeFileSync(__dirname + '/' + outFilenamePoints, JSON.stringify(pointDict));
fs.writeFileSync(__dirname + '/' + outFilenamePackets, JSON.stringify(packetDict));
