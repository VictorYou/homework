#!/bin/bash
sudo -u btsmed -s /opt/imp/`rpm -qa | grep nokia | cut -d "-" -f 3`/bin/imp-startup.sh getState<<-EOF
EOF