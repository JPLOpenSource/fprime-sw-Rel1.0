/**
  * getCouchDBDocs.js
  *
  * Use the CouchDB HTTP API to retrieve all openmct documents and write them
  * to a JSON file
  *
  * Author: Aaron Doubek-Kraft aaron.doubek-kraft@jpl.nasa.gov
  *
  **/

const http = require('http');
const config = require('../config');
const fs = require('fs');
const path = require('path');

const dbURL = config.client.persistence.url,
      database = {docs: []},
      outFilename = 'res/couchDBDocs.json';

function makeGetRequest(url) {
    return new Promise(function(resolve, reject) {
        http.get(url, (response) => {
            console.log(`GET ${url} : Status ${response.statusCode}`)

            let data = '';

            response.on('data', (chunk) => {
                data += chunk;
            });

            response.on('end', () => {
                resolve(data);
            });

            response.on('error', (err) => {
                reject(err);
            });
        });
    });
};

makeGetRequest(dbURL + '/_all_docs')
    .then( (allDocs) => {
        allDocsObj = JSON.parse(allDocs);
        rowPromises = [];
        allDocsObj.rows.forEach( (rowObj) => {
            let id = rowObj.id;
            rowPromises.push(makeGetRequest(dbURL + '/' + id));
        });
        return Promise.all(rowPromises);
    }).then( (rowData) => {
        console.log('All Objects Retrieved')
        rowData.forEach( (data) => {
            let dataObj = JSON.parse(data);
            delete dataObj._rev;
            database.docs.push(dataObj);
        });

        let outFilepath = path.dirname(__dirname) + '/' + outFilename;
        console.log(`Writing CouchDB data to ${outFilename}`);
        fs.writeFileSync(outFilepath, JSON.stringify(database, '', 4));
        process.exit();
    }).catch( (err) => {
        console.log(`ERROR: ${err.message}`);
        process.exit();
    });
