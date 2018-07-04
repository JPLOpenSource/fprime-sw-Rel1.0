var express = require('express');

function ClientRouter(options) {
    var router = express.Router();

    router.get('/config.json', function (req, res) {
        return res.json(options.persistence).end();
    });
    router.use('/openmct', express.static(__dirname + '/../../node_modules/openmct/dist'));
    router.use('/', express.static(__dirname + '/../../client'));

    return router;
}

module.exports = ClientRouter;
