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
	var socket = new WebSocket('ws://' + site + ':' + commandPort.toString());

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
			var commands = $.makeArray(arguments);
			console.log(commands);
			
			getDictionary().then(function(dict) {
				var usrCommands = {};
				commands.forEach(function (cmd) {
					// Get command
					var commandReq = dict["isf"]["commands"][cmd];
					var name = commandReq["name"];
					var cmdArgs = commandReq["arguments"];

					// Get arguments
					instance.output.write(name + ': ');
					// var userArgs = [];
					var inputs = [];
					cmdArgs.forEach(function (a) {

						instance.output.write('Enter ' + a['name'] + ' (' + a["description"] + ')');
						return instance.input.request().then(function(value) {
						    userArgs.push(value);
						});
					});

					usrCommands[cmd] = userArgs;
				});

				instance.output.write(JSON.stringify(usrCommands));
				base.deferred.resolve();
			});

			
			return base.deferred.promise();
			
		};

		return base;
	};
}