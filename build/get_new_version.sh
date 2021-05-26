#!/bin/bash -ex
set -ex

CURRENTDIR=$(dirname $0)
. "$CURRENTDIR"/function_build_app.sh

LATEST_VERSION=$(get_latest_version_from_git FastPass-Testing)
NEW_VERSION=$(get_next_version "$LATEST_VERSION")

echo -n "$NEW_VERSION"
