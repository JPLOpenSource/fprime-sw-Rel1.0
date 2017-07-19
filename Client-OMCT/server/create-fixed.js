// Create fixed display of all channels

var getIds = require('./deserializeIsf').getIds;
var fs = require('fs');

function CreateFixed() {

	var type = 'isf.taxonomy:';

	var idSize = getIds().length;
	var composition = getIds().map(function (id) {
		return type + id.toString()
	});

	var y = -1;
	var elements = [];
	composition.forEach(function (id) {
		y++;
		elements.push({
			"type": "fixed.telemetry",
			"x": 0,
			"y": y,
			"id": id,
			"stroke": "transparent",
			"color": "",
			"titled": true,
			"width": 8,
			"height": 1,
			"useGrid": true
		});
	});

	var fixed = {
		"mine": {
		  "name": "My Items",
		  "type": "folder",
		  "composition": [
		    "267f72c9-22c3-4d7c-ad5e-e471e76e71be"
		  ],
		  "location": "ROOT",
		  "modified": 1500501635491,
		  "persisted": 1500501635491
		},

		"267f72c9-22c3-4d7c-ad5e-e471e76e71be": {
			"layoutGrid": [
			  64,
			  idSize + 5
			],
			"composition": composition,
			"name": "Fixed Display Channels",
			"type": "telemetry.fixed",
			"configuration": {
				"fixed-display": {
					"elements": elements
				}
			},
			"modified": Date.now(),
			"location": "mine",
			"persisted": Date.now()
		}
	};

	fs.writeFile('server/res/fixed.json', JSON.stringify(fixed), function (err) {
		if (err) {
			console.log(err);

		}
	});
}

module.exports = CreateFixed;
