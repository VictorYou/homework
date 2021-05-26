#!/bin/bash -ex
set -ex

CURRENTDIR=$(dirname $0)
. "$CURRENTDIR"/function_build_fp_tvnf.sh

LATEST_VERSION=$(get_latest_version_from_git FastPass-Testing)

echo -n "$LATEST_VERSION"
