// Configure the time
const ONE_YEAR = 365 * 24 * 60 * 60 * 1000;
const ONE_MINUTE = 60 * 1000;

function SetTimeSystem() {
	return function (openmct) {
		openmct.plugins.Conductor({
		    menuOptions: [
	            // 'Fixed' bounds mode configuation for the UTCTimeSystem
	            {
	                timeSystem: 'utc',
	                bounds: {start: Date.now() - 30 * ONE_MINUTE, end: Date.now()},
	                zoomOutLimit: ONE_YEAR,
	                zoomInLimit: ONE_MINUTE
	            },
	            // Configuration for the LocalClock in the UTC time system
	            {
	                clock: 'local',
	                timeSystem: 'utc',
	                clockOffsets: {
	                	start: - 30 * ONE_MINUTE,
	                	end: 0
	                },
	                zoomOutLimit: ONE_YEAR,
	                zoomInLimit: ONE_MINUTE
	            },
	            //Configuration for the LocaLClock in the Local time system
	            {
	                clock: 'local',
	                timeSystem: 'local',
	                clockOffsets: {
	                	start: - 15 * ONE_MINUTE,
	                	end: 0
	                }
	            }
	        ]
		});

		openmct.time.clock('local', {
            start: -15 * 60 * 1000, 
            end: 0
        });
		// openmct.time.timeSystem('utc');	// Set timesystem
	}
}