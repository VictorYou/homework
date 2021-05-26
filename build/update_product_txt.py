import sys
import json
import re
import os

latest_product_txt=sys.argv[1]
product_properties_json=sys.argv[2]
new_version=sys.argv[3]
new_product_txt=sys.argv[4]

with open(latest_product_txt) as product_txt_file:
  product_txt = product_txt_file.read()

product_txt_parsed = json.loads(product_txt)

with open(product_properties_json) as product_properties_file:
  product_properties = product_properties_file.read()

product_properties_parsed = json.loads(product_properties)

new_version_product_txt = {}
filtered = {k: v for k, v in product_txt_parsed.items() if k != 'version' and k != 'artifacts'}
for key in filtered.keys():
  new_version_product_txt[key] = filtered[key]

new_version_product_txt['version'] = new_version
new_version_product_txt['artifacts'] = []

for artifact in [r for r in product_properties_parsed['results'] if r['name'] != 'product.txt']:
  artifact_hash={}
  artifact_hash["filename"] = artifact["name"]
  artifact_hash["md5sum"] = artifact["actual_md5"]
  artifact_hash["sha256sum"] = artifact["sha256"]
  artifact_hash["type"] = artifact["type"]
  artifact_hash["pathname"] = os.path.basename(artifact['path'])  
  search_version = re.search('\d+\.\d+\.\d+', artifact["name"])
  if search_version is not None:
    artifact_hash["version"] = search_version.group()
  else:
    artifact_hash["version"] = "0.0.0"
  new_version_product_txt['artifacts'].append(artifact_hash)

new_file = open(new_product_txt, 'w')
new_file.write(json.dumps(new_version_product_txt, indent=2, sort_keys=True))
new_file.close()
product_txt_file.close()
product_properties_file.close()
