import json
import os
import sys

filename = sys.argv[1]

with open(filename) as file:
  content = file.read()

data = json.loads(content)
common_config = { k: v for k, v in data['NeVeLabs'].items() if k == 'CommonConfig' }
data_to_save = {"NeVeLabs": common_config}

os.remove(filename)
with open(filename, 'w') as file:
  file.write(json.dumps(data_to_save, indent=2, sort_keys=True))
