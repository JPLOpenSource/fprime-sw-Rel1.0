// $(document).ready(function(){
//     $("#flip").click(function(){
//         $("#panel").slideToggle("slow");
//     });
// });

function SetupConsole() {

	// getDictionary().then(function (dict) {
		// let commandDict = dict['isf']['commands'];		
		// let validCommands = [];
		// for (id in commandDict) {
		// 	validCommands.push(commandDict[id]['name']);
		// }

		var command = new Vue({
			el: '#command',
			data: {
				cmd: '',
				cmdHist: [],
				history: ''
			},
			methods: {
				sendCmd: function (event) {
					if (event.key == "Enter" && this.cmd != '') {
						this.cmdHist.push(this.cmd);
						history = this.cmdHist.join('\n');
					}
				}
			}
		});
	// });

}