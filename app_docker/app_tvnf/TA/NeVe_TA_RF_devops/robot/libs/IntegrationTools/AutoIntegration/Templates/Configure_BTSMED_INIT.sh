#!/bin/bash
echo "==========Initializing BTSMED=========="
/usr/bin/expect <<-EOF
set timeout 120
spawn sudo -u Nemuadmin /opt/imp/`rpm -qa | grep nokia | cut -d "-" -f 3`/cli/bin/imp-cli-control.sh start
expect "btsmed>"
send "btsmed init --btsmedId init_id\r"
expect "proceed"
send "y\r"
expect "btsmed>"
send "exit\r"
expect eof
EOF
