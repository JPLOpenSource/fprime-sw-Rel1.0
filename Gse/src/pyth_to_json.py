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

if __name__ == "__main__":
	print cl.getChDescDict()