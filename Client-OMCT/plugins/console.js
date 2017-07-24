
$(document).ready(function() {	
	$('#faketerminal').faketerminal({
	    username: 'commander',
	    hostname: window.location.host,
	    history: 1000,
	    prompt: '%username%: '

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
			var args;
			commands.forEach(function (cmd) {
				
			});
			console.log(args);

			instance.

			base.deferred.resolve();
			return base.deferred.promise();
		};

		return base;
	};
}