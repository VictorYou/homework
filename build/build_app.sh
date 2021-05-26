#!/bin/bash -ex
set -ex

CURRENTDIR=$(dirname $0)
TOBUILDDIR="$CURRENTDIR/to_build_app"
. "$CURRENTDIR"/function_build_app.sh
set_proxy


push_or_pull_docker_image()
{
  local image_with_tag=$1             # fastpass-testing-docker-local.esisoj70.emea.nsn-net.net/busybox:1.0
  local registry_credential=$2        # viyou:APAPFXPBRnGcf7VoCk4x3AZXsJH 
  local action=$3                     # push # pull

  if [[ "$registry_credential" =~ ([a-zA-Z0-9]+):([a-zA-Z0-9]+) ]]; then
    local registry_user=${BASH_REMATCH[1]}
    local registry_token=${BASH_REMATCH[2]}
  else
    echo "wrong credential: $registry_credential, exiting"
    exit 1
  fi

  echo "$registry_token" | sudo docker login -u "$registry_user" --password-stdin \
  && sudo docker "$action" "$image_with_tag" \
  && sudo docker logout "$registry_repo"
}

push_docker_image()
{
  local image_with_tag=$1             # fastpass-testing-docker-local.esisoj70.emea.nsn-net.net/busybox:1.0
  local registry_credential=$2        # viyou:APAPFXPBRnGcf7VoCk4x3AZXsJH 
  push_or_pull_docker_image "$image_with_tag" "$registry_credential" "push"
}

pull_docker_image()
{
  local image_with_tag=$1             # netact-neve-docker-local.artifactory-espoo1.int.net.nokia.com/neveexecs/neveexec:master
  local registry_credential=$2        # viyou:APAPFXPBRnGcf7VoCk4x3AZXsJH 
  push_or_pull_docker_image "$image_with_tag" "$registry_credential" "pull"
}

build_app_docker()
{
  local new_product_version=$1                     # 0.0.9
  local registry_credential=$2                     # viyou:APAPFXPBRnGcf7VoCk4x3AZXsJH
  local image_name='app_docker'
  local folder='app_docker'
  local tag_name="$image_name"
  local latest_version=$(get_latest_version_from_git $tag_name)
  local tag="$tag_name.$latest_version"
  local latest_version_commit=$(git rev-list -n 1 $tag)
  local need_build=$(need_build "$latest_version_commit" "$folder")

  if [ "$need_build" != "" ]; then
    echo "===================== build tvnf ========================"
    local new_version=$(get_next_version "$latest_version")
    local registry_repo="viyou"
    local image_with_tag="$registry_repo/$image_name:$new_version"
    sudo docker rmi -f ubuntu:latest
    sudo docker build -t "$image_with_tag" --build-arg=http_proxy="http://10.144.1.10:8080/" --build-arg=https_proxy="http://10.144.1.10:8080/" $folder
    push_docker_image "$image_with_tag" "$registry_credential"
    sudo docker rmi "$image_with_tag"
    git tag "$image_name.$new_version" HEAD
    expect "$CURRENTDIR"/push_code
  else
    echo "no need to build, exiting"
    exit 1
  fi
}

main()
{
  local new_version=$1                             # 20.0.9
  local registry_credential=$2

  build_app_docker "$new_version" "$registry_credential"
}

if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  main "$@"
fi

exit 0
