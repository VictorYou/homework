#!/bin/bash -ex
set -ex

CURRENTDIR=$(dirname $0)

. "$CURRENTDIR"/../function_build_fp_tvnf.sh

function get_artifacts()
{
  local folder=$1
  local repo_name=$2
  local artifactory_url=$3
  local artifactory_credential=$4

  local search_string='items.find({"repo":{"$eq":"REPOSITORY_NAME"}, "path":{"$match":"FOLDER"}, "type":{"$eq":"file"}}).include("*")'
  search_string=$(echo "$search_string" | sed -r "s|FOLDER|$folder|" | sed -r "s|REPOSITORY_NAME|$repo_name|")

  artifacts=$(curl -u$artifactory_credential -X POST --header "content-type:text/plain" --data "$search_string" "$artifactory_url/artifactory/api/search/aql" -k | jq -r '.results[]' | jq -r '.name' | tr '\n' ',' | sed -r 's|,$||')
  echo -n $artifacts
}

function handle_artifacts()
{
  local handle_function=$1
  local artifacts_from=$2
  local artifacts_to=$3
  local folder=$4
  local repo_name=$5
  local artifactory_url=$6
  local artifactory_credential=$7

  OIFS=$IFS
  IFS=','
  for artifact in $artifacts_from; do
    local exists=$(echo $artifacts_to | grep $artifact)
    if [ -z "$exists" ]; then
      "$handle_function" "$artifact" "$folder" "$repo_name" "$artifactory_url" "$artifactory_credential"
    fi  
  done
  IFS=$OIFS
}

function copy_artifacts()
{
  local artifacts=$1                              # neveexec_master.0.0.9.tar.gz,testvnf_rest.0.0.24.tar
  local artifacts_acl=$2                          # neveexec_master.0.0.9.tar.gz,testvnf_rest.0.0.24.tar
  local folder_from=$3                            # NetAct/20.0.4/INSTALL_MEDIA
  local folder_to=$4                              # NetAct/temp
  local repo_from=$5                              # artifactory-edge-uploads
  local repo_to=$6                                # artifactory-edge-uploads
  local artifactory_url=$7                        # https://10.96.170.43
  local artifactory_credential=$8                 # admin:f1qb56hrH0QndKaO01m3hNszSpmcia

  OIFS=$IFS
  IFS=','
  for artifact in $artifacts; do
    local exists=$(artifact_exist "$folder_from" "$artifact" "$repo_from" "$artifactory_url" "$artifactory_credential")
    if [ -z "$exists" ]; then
      echo "$artifact under $dir_name does not exist, ignoring"
      continue
    fi
    exists=`echo $artifacts_acl | sed -r "/$artifact/!d"`
    if [ -z "$exists" ]; then
      echo "$artifact not in acceptance list: $artifacts_acl, ignoring"
      continue
    fi
    copy_artifact "$folder_from/$artifact" "$folder_to/$artifact" "$repo_from" "$repo_to" "$artifactory_url" "$artifactory_credential"
  done
  IFS=$OIFS
}

function copy_install_media_from_last_version()
{
  local artifacts_acl=$1                          # neveexec_master.0.0.9.tar.gz,testvnf_rest.0.0.24.tar
  local folder_to=$2                              # NetAct/20.0.4/INSTALL_MEDIA
  local repo_to=$3                                # artifactory-edge-uploads
  local artifactory_url=$4                        # https://10.96.170.43
  local artifactory_credential=$5                 # admin:f1qb56hrH0QndKaO01m3hNszSpmcia
  local latest_version_on_ndap=$(get_latest_version_from_ndap "$repo_to" NetAct "$artifactory_url" "$artifactory_credential")
  local latest_version_folder="NetAct/$latest_version_on_ndap/INSTALL_MEDIA"  # NetAct/20.0.4/INSTALL_MEDIA
  local artifacts_from_last_version_on_ndap=$(get_artifacts "$latest_version_folder" "$repo_to" "$artifactory_url" "$artifactory_credential")

  copy_artifacts "$artifacts_from_last_version_on_ndap" "$artifacts_acl" "$latest_version_folder" "$folder_to" "$repo_to" "$repo_to" "$artifactory_url" "$artifactory_credential"
}
