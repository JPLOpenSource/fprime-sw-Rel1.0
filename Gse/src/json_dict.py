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
	ch_cd[id]["id"]            = id
	ch_cd[id]["name"]          = cl.getNameDict()[id]
	ch_cd[id]["telem_type"]    = "channel"
	ch_cd[id]["component"]     = cl.getCompDict()[id]
	ch_cd[id]["description"]   = cl.getChDescDict()[id]
	ch_cd[id]["type"]         = cl.getTypesDict()[id].__repr__()
	ch_cd[id]["format_string"] = cl.getFormatStringDict()[id]

# Create event combined dictionary
ev_cd = {}
for id in el.getNameDict():
	ev_cd[id] = {}

for id in ev_cd:
	ev_cd[id]["id"]            = id
	ev_cd[id]["name"]          = el.getNameDict()[id]
	ev_cd[id]["telem_type"]    = "event"
	# ev_cd[id]["severity"]      = el.getSeverity()[id]
	ev_cd[id]["format_string"] = el.getFormatString()[id]
	arguments = [];
	for argument in el.getEventDesc()[id]:
		arg = argument[2].__repr__()
		if arg == 'Enum':
			enum_dict = {v:k for k,v in argument[2].enum_dict().iteritems()}
			arguments.append(enum_dict)
		else:
			arguments.append(arg)
	ev_cd[id]["arguments"] = arguments

final_dict = {
	"isf": {
		"channels": ch_cd,
		"events": ev_cd
	}
}

save = 'Client-OpenMCT-dev/plugins/dictionary.json'
with open(save, 'w') as fp:
	json.dump(final_dict, fp, sort_keys=True, indent=4)
 
if __name__ == "__main__":
	print save
