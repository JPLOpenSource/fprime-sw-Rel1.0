# Sanchit Sinha
# Create OpenMCT formatted dictionary of channels

import os
import sys
import json
from controllers import channel_loader, event_loader

# Set path
dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../generated/Ref'
sys.path.append(dir_path)

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

for id in ch_cd:
	ch_cd[id]["name"]        = cl.getNameDict()[id]
	ch_cd[id]["component"]   = cl.getCompDict()[id]
	ch_cd[id]["description"] = cl.getChDescDict()[id]
	ch_cd[id]["type"]        = cl.getTypesDict()[id]
	ch_cd[id]["format"]      = cl.getFormatStringDict()[id]
	ch_cd[id]["num_type"]    = (cl.getTypesDict()[id]).__repr__()

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

# Create event combined dictionary
ev_cd = {}
for id in el.getNameDict():
	ev_cd[id] = {}

for id in ev_cd:
	ev_cd[id]["name"]      = el.getNameDict()[id]
	ev_cd[id]["severity"]  = el.getSeverity()[id]
	ev_cd[id]["format"]    = el.getFormatString()[id]
	ev_cd[id]["arguments"] = el.getEventDesc()[id]

for id in ev_cd:
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
	arg_format = []
	for arg in ev_cd[id]["arguments"]:
		# Arg in format of tuple: (Title, Description, TypeClass)
		arg_type = arg[2].__repr__()
		if arg_type == "Enum":
			arg_format.append(arg[2].keys())
		else:
			arg_format.append(arg_type)

	to_append = {
		"name": ev_cd[id]["name"],
		"key": str(id),
		"num_type": "string",
		"str_format": ev_cd[id]["format"],
		"arg_format": arg_format,
		"values": [value_format, time_format]
	}

	telemetry.append(to_append)


final_dict = {
	"name": "ISF",
	"key": "isf",
	"measurements": telemetry,
}

save = 'node-clientView/client/isf-omct/res/dictionary.json'
with open(save, 'w') as fp:
	json.dump(final_dict, fp, sort_keys=True, indent=4)
 
if __name__ == "__main__":
	print save
