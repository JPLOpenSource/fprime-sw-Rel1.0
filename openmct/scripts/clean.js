/**
  * clean.js
  *
  * Cleanup generated resources associated with autocoder and builds scripts
  *
  * Author: Aaron Doubek-Kraft aaron.doubek-kraft@jpl.nasa.gov
  **/

const fs = require('fs');
const path = require('path');

const config = require('../config');

const filesToRemove = [path.dirname(__dirname) + '/' + config.dictionary.pointsFile,
                       path.dirname(__dirname) + '/' + config.dictionary.packetsFile,
                       path.dirname(__dirname) + '/res/dictionary.json'];

filesToRemove.forEach( (filename) => {

    fs.unlink(filename, (err) => {
        if (err) {
            console.log(`Remove failed: ${err.message}`)
        } else {
            console.log(`Successfully removed ${filename}`);
        }

    });
});
