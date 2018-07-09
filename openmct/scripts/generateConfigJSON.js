/*
    generateConfigJSON.js

    Given a JSON dictionary for an fprime app, generate JSON configuration
    files for the openmct bson server. Points file is saved in "points.json",
    packets file is saved in "packets.json"

    Author: Aaron Doubek-Kraft aaron.doubek-kraft@jpl.nasa.gov

*/

const fs = require('fs');
const path = require('path');

const dictJSON = fs.readFileSync(path.dirname(__dirname) + '/res/dictionary.json', {encoding: 'UTF-8'}),
      outFilenamePoints = 'res/points.json',
      outFilenamePackets = 'res/packets.json',
      dict = JSON.parse(dictJSON),
      deployment = Object.values(dict)[0],
      pointDict = {}
      packetDict = {
          "Channels": {
              name: "Channels",
              points: []
          }
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
let raw_value_format = {
    key: "raw_value",
    name: "Raw Value",
    hints: {"range":2}
};


Object.entries(deployment.channels).forEach(function (channel) {
    let id = channel[0],
        props = channel[1],
        name = props.name;

    packetDict['Channels'].points.push(name);
    pointDict[name] = {
        name: name,
        key: name,
        id: name,
        values: [time_format, name_format, raw_value_format]
    }
});

let outFilepathPoints = path.dirname(__dirname) + '/' + outFilenamePoints;
let outFilepathPackets = path.dirname(__dirname) + '/' + outFilenamePackets;

console.log(`Writing points config file to ${outFilenamePoints}`);
fs.writeFileSync(outFilepathPoints, JSON.stringify(pointDict));
console.log(`Writing packets config file to ${outFilenamePackets}`);
fs.writeFileSync(outFilepathPackets, JSON.stringify(packetDict));