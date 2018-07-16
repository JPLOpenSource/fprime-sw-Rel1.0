/**
  * setCouchDBDocs.js
  *
  *
  **/

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const config = require('../config');

const dbURL = new url.URL(config.client.persistence.url);

try {
    dbJSON = fs.readFileSync(path.dirname(__dirname) + '/res/couchDBDocs.json', {encoding: 'UTF-8'});
} catch (err) {
    console.log(err.message);
    process.exit();
}

const options = {
    hostname: dbURL.hostname,
    port: dbURL.port,
    path: dbURL.pathname + '/_bulk_docs',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(dbJSON)
    }
}

const req = http.request(options, (response) => {

    console.log(`POST ${dbURL.toString()} : Status ${response.statusCode}`);

    if (response.statusCode === 404) {
        console.log(`Resource not found. Make sure database ${dbURL.pathname} exists.`);
        return;
    }

    let data = '';

    response.on('data', (chunk) => {
        data += chunk;
    });

    response.on('end', () => {
        dataObj = JSON.parse(data)
        dataObj.forEach( (docUpdate) => {
            if (docUpdate.ok) {
                console.log(`Successfully added ${docUpdate.id} to database ${dbURL.pathname}`);
            } else if (docUpdate.error) {
                let err = `ERROR: Encountered issue '${docUpdate.reason}' while attempting to update ${docUpdate.id} in ${dbURL.pathname}`
                if (docUpdate.error === 'conflict') {
                    err += ' -- Document may already exist'
                }
                console.log(err);
            }
        });
    });

    response.on('error', (err) => {
        console.log(err.message);
    });
});

req.on('error', (err) => {
    let errMessage = `ERROR: ${err.message}.`;

    if (err.code === 'ECONNREFUSED') {
        errMessage += ` Make sure the CouchDB server is running at ${dbURL.host}.`
    }

    console.log(errMessage);
    req.end();
});

req.write(dbJSON);
req.end();
