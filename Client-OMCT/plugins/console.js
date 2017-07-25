
$(document).ready(function() {	
	$('#faketerminal').faketerminal({
	    username: 'commander',
	    hostname: window.location.host,
	    history: 1000,
	    prompt: '%username%: '

	});

	// Flip
	$("#flip").click(function() {
	    $("#faketerminal").slideToggle("fast");
	    $("#omct").height();
	});
});

function SetupCommands(site, commandPort) {
	var socket = new WebSocket('ws://' + site + ':' + commandPort.toString());
	var commands = http.get('/server/res/dictionary.json').then(function (result) {
		return result.data['commands'];
	});

	console.log(JSON.stringify(commands));

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

			instance.input

			base.deferred.resolve();
			return base.deferred.promise();
		};

		return base;
	};
}