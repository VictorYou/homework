import os
import sys
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom

filename = sys.argv[1]
with open(filename) as file:
  tree = ET.parse(file)

root = tree.getroot()
for ne in root.findall('./*'):
  if not re.match('common_for', ne.tag):
    root.remove(ne)

rough_string = ET.tostring(root, 'utf-8')
parsed = xml.dom.minidom.parseString(rough_string)
pretty_string = parsed.toprettyxml(indent="\t")

os.remove(filename)
with open(filename, 'w') as file:
  file.write(pretty_string)
