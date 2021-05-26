import sys
import json
import re

latest_artifact_list_txt=sys.argv[1]
new_artifacts=sys.argv[2]
new_version=sys.argv[3]
new_artifact_list_txt=sys.argv[4]

with open(latest_artifact_list_txt) as artifact_list_txt_file:
  artifact_list_txt = artifact_list_txt_file.read()

artifact_list_parsed = json.loads(artifact_list_txt)
artifact_list_parsed['version'] = new_version

new_artifact_list = new_artifacts.split(',')

# if there is new artifact, it replaces the old one
for artifact in artifact_list_parsed["artifacts"]:
  old_name = re.split('\.', artifact['filename'])[0]
  for new_artifact in new_artifact_list:
    m = re.search(old_name, new_artifact)
    if m:
      artifact['filename'] = new_artifact
      new_artifact_list.remove(new_artifact)

# add unmatched artifact as newly added ones
for new_artifact in new_artifact_list:
  if new_artifact != '':
    artifact_list_parsed["artifacts"].append({'filename': new_artifact})

with open(new_artifact_list_txt, 'w') as new_file:
  new_file.write(json.dumps(artifact_list_parsed, indent=2, sort_keys=True))
