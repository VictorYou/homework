#!/bin/bash -ex
set -ex

CURRENTDIR=$(dirname $0)

. "$CURRENTDIR"/../function_build_fp_tvnf.sh
. "$CURRENTDIR"/function.sh

set_proxy

function main()
{
  local artifacts_from=$(get_artifacts "NetAct/$FOLDER_FROM/INSTALL_MEDIA" "$PRODUCT_REPO_NAME_FROM" "$ARTIFACTORY_FROM" "$CREDENTIAL_FROM")
  handle_artifacts download_file "$artifacts_from" "" "NetAct/$FOLDER_FROM/INSTALL_MEDIA" "$PRODUCT_REPO_NAME_FROM" "$ARTIFACTORY_FROM" "$CREDENTIAL_FROM"
  handle_artifacts upload_file "$artifacts_from" "" "NetAct/deployment/INSTALL_MEDIA" "$REPO_NAME_TO" "$ARTIFACTORY_TO" "$CREDENTIAL_TO"

  local metadata_from=$(get_artifacts "NetAct/$FOLDER_FROM/METADATA" "$PRODUCT_REPO_NAME_FROM" "$ARTIFACTORY_FROM" "$CREDENTIAL_FROM")
  handle_artifacts download_file "$metadata_from" "" "NetAct/$FOLDER_FROM/METADATA" "$PRODUCT_REPO_NAME_FROM" "$ARTIFACTORY_FROM" "$CREDENTIAL_FROM"
  handle_artifacts upload_file "$metadata_from" "" "NetAct/deployment/METADATA" "$REPO_NAME_TO" "$ARTIFACTORY_TO" "$CREDENTIAL_TO"
}

PRODUCT_REPO_NAME_FROM=$1
FOLDER_FROM=$2
ARTIFACTORY_FROM=$3
CREDENTIAL_FROM=$4
REPO_NAME_TO=$5
ARTIFACTORY_TO=$6
CREDENTIAL_TO=$7

main

exit 0
