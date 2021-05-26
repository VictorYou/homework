#!/bin/bash -ex
set -ex

CURRENTDIR=$(dirname $0)
TOBUILDDIR="$CURRENTDIR/to_build_app"
. "$CURRENTDIR"/function_build_fp_tvnf.sh
set_proxy




push_or_pull_docker_image()
{
  local image_with_tag=$1             # fastpass-testing-docker-local.esisoj70.emea.nsn-net.net/busybox:1.0
  local registry_credential=$2        # viyou:APAPFXPBRnGcf7VoCk4x3AZXsJH 
  local action=$3                     # push # pull
  local registry_repo=${image_with_tag%%/*}     # fastpass-testing-docker-local.esisoj70.emea.nsn-net.net

  if [[ "$registry_credential" =~ ([a-zA-Z0-9]+):([a-zA-Z0-9]+) ]]; then
    local registry_user=${BASH_REMATCH[1]}
    local registry_token=${BASH_REMATCH[2]}
  else
    echo "wrong credential: $registry_credential, exiting"
    exit 1
  fi

  echo "$registry_token" | sudo docker login -u "$registry_user" --password-stdin "$registry_repo" \
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
  local new_product_version=$1                     # 20.0.9
  local repo_name=$2                               # FastPass-Testing-local
  local artifactory_url=$3                         # https://esisoj70.emea.nsn-net.net:443
  local artifactory_credential=$4                  # ca_fp_devops:Welcome123
  local registry_credential=$5                     # viyou:APAPFXPBRnGcf7VoCk4x3AZXsJH
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
    local registry_repo="fastpass-testing-docker-local.esisoj70.emea.nsn-net.net"
    local image_with_tag="$registry_repo/$image_name:$new_version"
    local image_to_copy="$image_name.$new_version.tar"
    sudo docker rmi -f ubuntu:latest
    cd app_tvnf_docker/app_tvnf/TA; sh build_ta_zip.sh; cd - 
    sudo docker build -t "$image_with_tag" $folder
#    push_docker_image "$image_with_tag" "$registry_credential"
    sudo docker save "$image_with_tag" > "$image_to_copy"
    sudo docker rmi "$image_with_tag"
    upload_file "$image_to_copy" "NetAct/artifacts/$image_name" "$repo_name" "$artifactory_url" "$artifactory_credential"
    git tag "$image_name.$new_version" HEAD
    git push --tags
  else
    image_to_copy="$image_name.$latest_version.tar"
  fi
# comment out to speed up testing
  copy_artifact "NetAct/artifacts/$image_name/$image_to_copy" "NetAct/$new_product_version/INSTALL_MEDIA/$image_to_copy" "$repo_name" "$repo_name" "$artifactory_url" "$artifactory_credential"
}

build_chart()
{
  local new_product_version=$1                     # 20.0.9
  local repo_name=$2                               # FastPass-Testing-local
  local artifactory_url=$3                         # https://esisoj70.emea.nsn-net.net:443
  local artifactory_credential=$4                  # ca_fp_devops:Welcome123
  local registry_credential=$5                     # viyou:APAPFXPBRnGcf7VoCk4x3AZXsJH
  local image_name='chart'
  local folder='app_chart'
  local tag_name="$image_name"
  local latest_version=$(get_latest_version_from_git $tag_name)
  local tag="$tag_name.$latest_version"
  local latest_version_commit=$(git rev-list -n 1 $tag)
  local need_build=$(need_build "$latest_version_commit" "$folder")

  if [ "$need_build" != "" ]; then
    echo "===================== build tvnf ========================"
    local new_version=$(get_next_version "$latest_version")
    local image_to_copy="$image_name.$new_version.tar"
    local image_to_copy="$image_name.$new_version.tar"
    tar cvf "$image_to_copy" "$folder"
    upload_file "$image_to_copy" "NetAct/artifacts/$image_name" "$repo_name" "$artifactory_url" "$artifactory_credential"
    git tag "$image_name.$new_version" HEAD
    git push --tags
  else
    image_to_copy="$image_name.$latest_version.tar"
  fi
  copy_artifact "NetAct/artifacts/$image_name/$image_to_copy" "NetAct/$new_product_version/INSTALL_MEDIA/$image_to_copy" "$repo_name" "$repo_name" "$artifactory_url" "$artifactory_credential"
}

update_ta_image()
{
  local new_product_version=$1                     # 20.0.9
  local update_image=$2
  local repo_name=$3                               # FastPass-Testing-local
  local artifactory_url=$4                         # https://esisoj70.emea.nsn-net.net:443
  local artifactory_credential=$5                  # ca_fp_devops:Welcome123
  local neve_registry_credential=$6                # viyou:APAPFXPBRnGcf7VoCk4x3AZXsJH
  local registry_credential=$7                     # viyou:APAPFXPBRnGcf7VoCk4x3AZXsJH
  local latest_neve=$(get_neve_build)
  local latest_version=$(get_artifact_version "$latest_neve")
  local image_name_to='neveexec_master'

  if [ "$update_image" = "yes" ]; then
    echo "===================== update ta image ========================"
    local new_version=$(get_next_version "$latest_version")
    local image_to_copy="$image_name_to.$new_version.tar"
    local image_name_from='neveexecs/neveexec'
    local registry_repo_from="netact-neve-docker-local.artifactory-espoo1.int.net.nokia.com"
    local image_from_with_tag="$registry_repo_from/$image_name_from:master"
    local registry_repo="fastpass-testing-docker-local.esisoj70.emea.nsn-net.net"
    local image_to_with_tag="$registry_repo/$image_name_to:$new_version"

    pull_docker_image "$image_from_with_tag" "$neve_registry_credential" \
    && sudo docker save -o "$image_to_copy" "$image_from_with_tag"\
    && sudo chmod 777 "$image_to_copy"
    upload_file "$image_to_copy" "NetAct/artifacts/$image_name_to" "$repo_name" "$artifactory_url" "$artifactory_credential"
    sudo rm -rf "$image_to_copy"

    sudo docker tag "$image_from_with_tag" "$image_to_with_tag"
    push_docker_image "$image_to_with_tag" "$registry_credential"
    git tag "$image_name_to.$new_version" HEAD
    git push --tags
  else
    image_to_copy="$image_name_to.$latest_version.tar"
  fi
  copy_artifact "NetAct/artifacts/$image_name_to/$image_to_copy" "NetAct/$new_product_version/INSTALL_MEDIA/$image_to_copy" "$repo_name" "$repo_name" "$artifactory_url" "$artifactory_credential"
}

main()
{
  local new_version=$1                             # 20.0.9
  local repo_name=$2                               # FastPass-Testing-local
  local artifactory_url=$3                         # https://esisoj70.emea.nsn-net.net:443
  local artifactory_credential=$4                  # ca_fp_devops:Welcome123
  local update_neve_image=$5                       # no
  local neve_registry_credential=$6
  local registry_credential=$7

  build_app_docker "$new_version" "$repo_name" "$artifactory_url" "$artifactory_credential" "$registry_credential"
  build_chart "$new_version" "$repo_name" "$artifactory_url" "$artifactory_credential"

}

if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  main "$@"
fi

exit 0
