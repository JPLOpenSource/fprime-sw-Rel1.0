function getDictionary() {
    // Needs directory from root of application
    return http.get('/server/res/dictionary.json').then(function (result) {
        return result.data;
    });
}

$(document).ready(function() {	
	$('#faketerminal').faketerminal({
	    username: 'commander',
	    hostname: window.location.host,
	    history: 1000,
	    prompt: '%username%: '
	});
	$("#flip").click(function() {
	    $("#faketerminal").slideToggle("fast");
	});
});


function SetupCommands(site, commandPort) {
	// var socket = new WebSocket('ws://' + site + ':' + commandPort.toString());

	window.FakeTerminal.command.send = function(instance) {
		window.FakeTerminal.command.apply(this, arguments);
		var base = this;
		// Add description
		base.info = function() {
			return {
				private: false,
				description: "Sends commands to netserver"
			};
		};

		// Execution
		base.execute = function() {


			// Print list of commands
			var command = $.makeArray(arguments)[0];
			console.log(command);
			
			getDictionary().then(function(dict) {
				// Get command
				var commandReq = dict["isf"]["commands"][command];
				var name = commandReq["name"];
				var cmdArgs = commandReq["arguments"];
				instance.output.write('Enter arguments for ' + name + ':');

				console.log(JSON.stringify(commandReq));

				var userArgs = [];
				var GetCmdArg = function () {
					return instance.input.request().then((value) => userArgs.push(value));
				};

				// var end = function () {
				// 	return Promise.resolve().then(function () {
				// 		instance.output.write(userArgs);
				// 		return base.deferred.resolve();
				// 	});
				// };

				var cmdProm = [];

				cmdArgs.forEach(function (a) {
					cmdProm.push(GetCmdArg);
				});

				cmdProm.push(base.deferred.resolve);

				cmdProm.reduce(function (prev, cur, i) {
					console.log(i);
					if (i !== cmdProm.length) {
						instance.output.write('Enter ' + cmdArgs[i]['name'] + ' (' + cmdArgs[i]["description"] + '):');
					} else {
						instance.output.write(userArgs);
					}
					return prev.then(cur);
				});

			});

			// var test = function () {
			// 	instance.output.write('hi');
			// 	return instance.input.request().then(function (value) {
			// 		instance.output.write(value);
			// 	});
			// }

			// test().then(() => test()).then(() => base.deferred.resolve());
			// var a = [test, test, base.deferred.resolve];

			// var prom = a[0]();
			// for (var i = 1; i < a.length; i++) {
			// 	prom = prom.then(a[i]);
			// }
			// a.reduce(function (prev, cur) {
			// 	return prev.then(cur);
			// }, test());
			
			// base.deferred.resolve();
			return base.deferred.promise();
			
		};

		return base;
	};
}