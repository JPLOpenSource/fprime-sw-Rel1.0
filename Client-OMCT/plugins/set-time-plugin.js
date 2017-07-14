// Configure the time
const ONE_YEAR = 365 * 24 * 60 * 60 * 1000;
const ONE_MINUTE = 60 * 1000;

function SetTimeSystem() {
	return function (openmct) {
		// openmct.plugins.Conductor({
	 //    	menuOptions: [
		//         {
		//             name: "Fixed",
		//             timeSystem: 'utc',
		//             bounds: {
		//                 start: Date.now() - 30 * ONE_MINUTE,
		//                 end: Date.now()
		//             }
		//         },
		//         {
		//             name: "Realtime",
		//             timeSystem: 'utc',
		//             clock: 'local',
		//             clockOffsets: {
		//                 start: -25 * ONE_MINUTE,
		//                 end: 5 * ONE_MINUTE
		//             }
		//         }
		//     ]
		// });

		// Configure clock
		openmct.time.clock('local', {
            start: -30 * ONE_MINUTE, 
            end: 0
        });
		// openmct.time.timeSystem('utc');	// Set timesystem
	}
}