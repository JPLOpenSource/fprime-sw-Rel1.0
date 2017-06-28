# Sanchit Sinha
# Create OpenMCT formatted dictionary of channels

import os
import sys
from controllers import channel_loader


dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../generated/Ref/channels'
sys.path.append(dir_path + "/../")
print dir_path
cl = channel_loader.ChannelLoader.getInstance()
cl.create(dir_path)

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


if __name__ == "__main__":
	print combined_dict