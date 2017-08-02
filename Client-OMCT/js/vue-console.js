// $(document).ready(function(){
//     $("#flip").click(function(){
//         $("#panel").slideToggle("slow");
//     });
// });

function SetupConsole() {
	let cmdHist = [];

	var command = new Vue({
		el: '#command',
		data: {
			cmd: ''
		},
		methods: {
			sendCmd: function (event) {
				if (event.key == "Enter") {
					cmdHist.push(this.cmd);
				}
			}
		}
	});

	

}