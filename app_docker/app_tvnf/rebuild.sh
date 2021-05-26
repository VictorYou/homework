#!/bin/bash

tvnf=${1:-10.55.76.110}
sshopts="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa"
rm -rf testvnf_rest.zip
zip -r testvnf_rest.zip testvnf_rest/

ssh $sshopts cloudadmin@$tvnf "[ ! -e ~/.kube ] && mkdir -p ~/.kube/"
ssh $sshopts cloudadmin@$tvnf "[ ! -e ~/.kube/config ] && sudo -E kubectl config view --raw >~/.kube/config" 
ssh $sshopts cloudadmin@$tvnf "sudo chmod 777 /mnt/appimage/app_tvnf"

echo "copy testvnf_rest.zip to tvnf"
scp $sshopts testvnf_rest.zip cloudadmin@$tvnf:/mnt/appimage/app_tvnf

echo "recreate tvnf"
if ! ssh $sshopts cloudadmin@$tvnf "cd /mnt/appimage/app_tvnf; sudo -E helm del tvnf; sudo rm -rf testvnf_rest/; sudo unzip testvnf_rest.zip; sleep 30; sudo -E helm install tvnf ../app_helm/testvnf-rest/"; then
  echo "cannot restart testvnf"
  exit 1
fi
