# Sanchit Sinha
# Create OpenMCT formatted dictionary of channels

import os
import sys
import json
from controllers import channel_loader

# Create channel loader object
dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../generated/Ref/channels'
sys.path.append(dir_path + "/../")
print dir_path
cl = channel_loader.ChannelLoader.getInstance()
cl.create(dir_path)

# Create combined dictionary
combined_dict = {}
for id in cl.getNameDict():
	combined_dict[id] = {}
	combined_dict[id]["name"] = cl.getNameDict()[id]

for id in combined_dict:
	combined_dict[id]["component"] = cl.getCompDict()[id]

for id in combined_dict:
	combined_dict[id]["description"] = cl.getChDescDict()[id]

for id in combined_dict:
	combined_dict[id]["type"] = cl.getTypesDict()[id]

for id in combined_dict:
	combined_dict[id]["format"] = cl.getFormatStringDict()[id]

for id in combined_dict:
	combined_dict[id]["num_type"] = (cl.getTypesDict()[id]).__repr__()

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


telemetry = []
for id in combined_dict:
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
	num_type = combined_dict[id]["num_type"]
	if num_type.find('F') != -1:
		value_format["format"] = "float"
	telemetry.append({
		"name": combined_dict[id]["name"],
		"key": str(id),
		"num_type": combined_dict[id]["num_type"],
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
# 	# print final_dict
