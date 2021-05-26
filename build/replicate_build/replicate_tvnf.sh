#!/bin/bash -ex
set -ex

CURRENTDIR=$(dirname $0)

. "$CURRENTDIR"/../function_build_fp_tvnf.sh
. "$CURRENTDIR"/function.sh

set_proxy

function main()
{
  local test_repo_name_from=$1    # FastPass-Testing-local
  local artifactory_from=$2       # https://esisoj70.emea.nsn-net.net:443
  local credential_from=$3        # ca_fp_devops:Welcome123
  local repo_name_to=$4           # artifactory-edge-uploads
  local artifactory_to=$5         # https://10.96.170.43
  local credential_to=$6          # admin:f1qb56hrH0QndKaO01m3hNszSpmcia
  local latest_version=$(get_latest_version_from_git FastPass-Testing)

  local artifacts_from=$(get_artifacts "NetAct/$latest_version/INSTALL_MEDIA" "$test_repo_name_from" "$artifactory_from" "$credential_from")
  copy_install_media_from_last_version "$artifacts_from" "NetAct/$latest_version/INSTALL_MEDIA" "$repo_name_to" "$artifactory_to" "$credential_to"
  local artifacts_to=$(get_artifacts "NetAct/$latest_version/INSTALL_MEDIA" "$repo_name_to" "$artifactory_to" "$credential_to")
  handle_artifacts download_file "$artifacts_from" "$artifacts_to" "NetAct/$latest_version/INSTALL_MEDIA" "$test_repo_name_from" "$artifactory_from" "$credential_from"
  handle_artifacts upload_file "$artifacts_from" "$artifacts_to" "NetAct/$latest_version/INSTALL_MEDIA" "$repo_name_to" "$artifactory_to" "$credential_to"

  for folder in "METADATA" "WORKFLOWS" "deployment"; do
    local artifacts_from=$(get_artifacts "NetAct/$latest_version/$folder" "$test_repo_name_from" "$artifactory_from" "$credential_from")
    local artifacts_to=$(get_artifacts "NetAct/$latest_version/$folder" "$repo_name_to" "$artifactory_to" "$credential_to")
    handle_artifacts download_file "$artifacts_from" "$artifacts_to" "NetAct/$latest_version/$folder" "$test_repo_name_from" "$artifactory_from" "$credential_from"
    handle_artifacts upload_file "$artifacts_from" "$artifacts_to" "NetAct/$latest_version/$folder" "$repo_name_to" "$artifactory_to" "$credential_to"
  done
}


if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  main "$@"
fi
