# Sanchit Sinha
# Create OpenMCT formatted dictionary of channels

import os
import sys
import json
from controllers import channel_loader, event_loader

# Set path
dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../generated/Ref'
sys.path.append(dir_path)
print dir_path

# Create channel loader object
cl = channel_loader.ChannelLoader.getInstance()
cl.create(dir_path + '/channels')

# Create event loader object
el = event_loader.EventLoader.getInstance()
el.create(dir_path + '/events')

# Create channel combined dictionary
ch_cd = {}
for id in cl.getNameDict():
	ch_cd[id] = {}
	ch_cd[id]["name"] = cl.getNameDict()[id]

for id in ch_cd:
	ch_cd[id]["component"] = cl.getCompDict()[id]

for id in ch_cd:
	ch_cd[id]["description"] = cl.getChDescDict()[id]

for id in ch_cd:
	ch_cd[id]["type"] = cl.getTypesDict()[id]

for id in ch_cd:
	ch_cd[id]["format"] = cl.getFormatStringDict()[id]

for id in ch_cd:
	ch_cd[id]["num_type"] = (cl.getTypesDict()[id]).__repr__()

# Create event combined dictionary
ev_cd = {}
for id in el.getNameDict():
	ev_cd[id] = {}
	ev_cd[id]["name"] = el.getNameDict()[id]

for id in ev_cd:
	ev_cd[id]["severity"] = el.getSeverity()[id]

for id in ev_cd:
	ev_cd[id]["format"] = el.getFormatString()[id]

for id in ev_cd:
	ev_cd[id]["description"] = el.getEventDesc()[id]

# Formatting for telemetry data
time_format = {
	"key": "utc",
    "source": "timestamp",
    "name": "Timestamp",
    "format": "utc",
    "hints": {
        "domain": 1
    }
}

# Add telemetry to combined channel dictionary
telemetry = []
for id in ch_cd:
	value_format = {
	    "hints": {
	        "range": 1
	    }, 
	    "key": "value", 
	    "max": 100, 
	    "min": 0, 
	    "name": "Value", 
	    "units": "units"
	}

	# determine format
	num_type = ch_cd[id]["num_type"]
	if num_type.find('F') != -1:
		value_format["format"] = "float"
	telemetry.append({
		"name": ch_cd[id]["name"],
		"key": str(id),
		"num_type": ch_cd[id]["num_type"],
		"values": [value_format, time_format]
	})

final_dict = {
	"name": "ISF",
	"key": "isf",
	"measurements": telemetry
}

with open('node-clientView/client/isf-omct/res/dictionary.json', 'w') as fp:
	json.dump(final_dict, fp, sort_keys=True, indent=4)
 
# if __name__ == "__main__":
# 	print final_dict
