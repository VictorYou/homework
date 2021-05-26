#!/bin/bash -ex
set -ex

CURRENTDIR=$(dirname $0)
TOBUILDDIR="$CURRENTDIR/to_build_configs"

. "$CURRENTDIR"/function_build_fp_tvnf.sh

set_proxy

NEW_VERSION=$1
REPO_NAME=$2
ARTIFACTORY_URL=$3
ARTIFACTORY_CREDENTIAL=$4

echo "====== get artifacts list, old and new ============="
NEW_FILES=$(get_files_to_build "$TOBUILDDIR")

[ -z "$NEW_FILES" ] && echo "no new config files, skipping"

echo "====== if there is new workflow file, move it to new version folder ========="
WORKFLOWDIR="$CURRENTDIR/../configs_workflows"
for file in $WORKFLOWDIR/*.gvy; do
  handle_workflow_file "$file" "$NEW_VERSION" "$REPO_NAME" "$ARTIFACTORY_URL" "$ARTIFACTORY_CREDENTIAL"
done

echo "====== if there is new deployment file, move it to new version folder ========="
DEPLOYMENTDIR="$CURRENTDIR/../configs_deployment"
for file in $DEPLOYMENTDIR/*; do
  handle_deployment_file "$file" "$NEW_VERSION" "$REPO_NAME" "$ARTIFACTORY_URL" "$ARTIFACTORY_CREDENTIAL"
done

echo "====== upload content.txt ========="
upload_file "$CURRENTDIR/../configs_metadata/content.txt" "NetAct/$NEW_VERSION/METADATA" "$REPO_NAME" "$ARTIFACTORY_URL" "$ARTIFACTORY_CREDENTIAL"

echo "====== create product.txt for new version and upload ========"
TEMPLATE_PRODUCT_TXT="$CURRENTDIR/../configs_metadata/product.txt"
NEW_PROPERTIES_FILE=$(get_artifact_properties "$NEW_VERSION" "$REPO_NAME" "$ARTIFACTORY_URL" "$ARTIFACTORY_CREDENTIAL")
python "$CURRENTDIR/update_product_txt.py" "$TEMPLATE_PRODUCT_TXT" "$NEW_PROPERTIES_FILE" "$NEW_VERSION" "product.txt" 
upload_file "product.txt" "NetAct/$NEW_VERSION/METADATA" "$REPO_NAME" "$ARTIFACTORY_URL" "$ARTIFACTORY_CREDENTIAL"
#save_artifact_to_local "product.txt" "$LOCAL_ARCHIVE_ARTIFACTS/product_txt"

exit 0
