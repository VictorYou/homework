#!/bin/bash -ex

CURRENTDIR=$(dirname $0)
LOCAL_ARCHIVE="/home/viyou/data/artifactory/$REPOSITORY_NAME"
LOCAL_ARCHIVE_ARTIFACTS=$LOCAL_ARCHIVE'/artifacts'

# check if build is needed
need_build()
{
  local latest_version_commit=$1
  local folder=$2
  if [ ! -z $latest_version_commit ] && [ ! -z "$folder" ]; then
    git log --pretty=format:"%H" "$latest_version_commit"..HEAD -- "$folder"
  fi
}

# compare version like 0.0.5
compare_version()
{
  version1=$1
  version2=$2
  OIFS=$IFS
  IFS='.';
  for i in $version1; do
    head2=${version2%%.*}
    if [ "$i" -lt "$head2" ]; then
      echo smaller
      return
    elif [ "$i" -gt "$head2" ]; then
      echo bigger
      return
    fi
    version2=${version2#${head2}.}
  done
  echo "equal"
  IFS=$OIFS
}

# get latest version
get_latest_version()
{
  local versions=$1               # 19.0.0,19.0.1,20.0.0
  local latest_version="0.0.0"

  OIFS=$IFS
  IFS=','
  for version in $versions; do
    version=$(echo $version | sed -r 's|([0-9]+\.[0-9]+\.[0-9]+)|\1|')
    compare=$(compare_version $version $latest_version)
    if [ "$compare" = "bigger" ]; then
      latest_version=$version 
    fi  
  done
  IFS=$OIFS
  echo "$latest_version"
}

get_latest_version_from_git()
{
  local name=$1                          # FastPass-Testing
  local search_string='/NAME\.[0-9]+.[0-9]+.[0-9]+.*/!d;s/.*\.([0-9]+\.[0-9]+\.[0-9]+).*/\1/'

  search_string=$(echo $search_string | sed -r "s|NAME|$name|g")
  versions=$(git tag | sed -r $search_string | tr '\n' ',' | sed 's|,$||')
  latest_version=$(get_latest_version $versions)
  echo "$latest_version"
}

get_latest_version_from_ndap()
{
  local repo=$1                          # artifactory-edge-uploads
  local folder=$2                        # NetAct
  local artifactory_url=$3               # https://10.96.170.43
  local credential=$4                    # admin:f1qb56hrH0QndKaO01m3hNszSpmcia

  search_string=$(echo $search_string | sed -r "s|NAME|$name|g")
  versions=$(curl -u$credential -sfk "$artifactory_url/artifactory/api/storage/$repo/$folder" | python -c 'import sys,json,re; \
  data=json.load(sys.stdin); \
  versions = [x["uri"][1:] for x in data["children"] if re.match("\d+.\d+\.\d+", x["uri"][1:])] ; \
  print(",".join(versions))')
  latest_version=$(get_latest_version $versions)
  echo "$latest_version"
}

get_artifact_properties()
{
  local version=$1
  local repo_name=$2
  local artifactory_url=$3
  local artifactory_credential=$4
  local filename="artifact_properties.$version.json"

  local search_string='items.find({"repo":{"$eq":"REPOSITORY_NAME"}, "path":{"$match":"NetAct/VERSION/*"}, "type":{"$eq":"file"}}).include("*")'
  search_string=$(echo "$search_string" | sed -r "s|VERSION|$version|" | sed -r "s|REPOSITORY_NAME|$repo_name|")

  curl -u$artifactory_credential -X POST --header "content-type:text/plain" --data "$search_string" "$artifactory_url/artifactory/api/search/aql" -k > $filename
  echo "$filename"
}

get_tvnf_build()
{
  local latest_version=$(get_latest_version_from_git 'fastpass_tvnf')
  echo "fastpass_tvnf.$latest_version.qcow2"
}

get_testvnf_rest_build()
{
  local latest_version=$(get_latest_version_from_git 'testvnf_rest')
  echo "fastpass_tvnf_app.$latest_version.tar"
}

get_neve_build()
{
  local latest_version=$(get_latest_version_from_git 'neveexec_master')
  echo "neveexec_master.$latest_version.tar.gz"
}

get_vnfd_build()
{
  local latest_version=$(get_latest_version_from_git 'VNFD')
  echo "VNFD.$latest_version.zip"
}

# get artifact version
get_artifact_version()
{
  local artifact=$1
  echo "$artifact" | sed -r 's|([^.-]+)[-.](([0-9]+\.)+)(.*)|\2|' | sed -r 's|\.$||'
}

# get new version
get_next_version()
{
  local version=$1
  version_tail=${version##*.}
  version_head=${version%${version_tail}}
  version_tail=$((version_tail+1))
  echo $version_head$version_tail
}

artifact_exist()
{
  local path=$1
  local file=$2
  local repo_name=$3
  local artifactory_url=$4
  local artifactory_credential=$5

  local search_string='items.find({"repo":{"$eq":"REPOSITORY_NAME"}, "path":{"$match":"ARTIFACTORY_PATH"}, "$or": [{"type":{"$eq":"folder"}}, {"type":{"$eq":"file"}}]}).include("*")'
  search_string=$(echo "$search_string" | sed -r "s|ARTIFACTORY_PATH|$path|" | sed -r "s|REPOSITORY_NAME|$repo_name|")
  exists=$(curl -u$artifactory_credential -X POST --header "content-type: text/plain" --data "$search_string" "$artifactory_url/artifactory/api/search/aql" -k | jq -r '.results[]' | jq -r '.name' | grep "$file")
  echo $exists
}

# check files under to_build folder
get_files_to_build()
{
  local dir=$1

  ls $dir | tr '\n' ',' | sed 's|,$||'
}

# combine artifact lists
combine_artifacts()
{
  local files=""

  for i in $*; do
    files=$files","$i
  done
  echo "$files" | sed -r 's|,$||' | sed -r 's|^,||'
}

# check config files under to_build folder
get_configs_to_build()
{
  combine_artifacts $*
}

# check artifacts to build vnf image
get_artifacts_to_build()
{
  local files=$1
  local configs=$2

  if [ -z "$configs" ]; then
    echo "$files"
    return
  fi

  configs=$configs","
  while [ ! -z "$configs" ]; do
    config=$(echo $configs | sed -r 's|([^,]*)(.*)|\1|')
    files=$(echo $files | sed -r "s|(.*)($config,*)(.*)|\1\3|" | sed -r 's|,$||')
    configs=${configs#$config,}
  done
  echo $files
}

# copy artifacts to artifacts folder for future use
copy_artifact()
{
  local file_from=$1                       # NetAct/artifacts/testvnf_rest/testvnf_rest.0.0.23.tar
  local file_to=$2                         # NetAct/20.0.4/INSTALL_MEDIA/testvnf_rest.0.0.24.tar
  local repo_from=$3                       # FastPass-Testing-local
  local repo_to=$4                         # FastPass-Testing-local
  local artifactory_url=$5                 # https://esisoj70.emea.nsn-net.net:443
  local artifactory_credential=$6          # ca_fp_devops:Welcome123

  local file_name=${file_from##*/}
  local dir_name=${file_from%/*}

  local exists=$(artifact_exist "$dir_name" "$file_name" "$repo_from" "$artifactory_url" "$artifactory_credential")
  if [ -z "$exists" ]; then
    print "$file_name under $dir_name does not exist, exiting"
    exit -1
  fi
  curl -u$artifactory_credential -X POST "$artifactory_url/artifactory/api/copy/$repo_from/$file_from?to=/$repo_to/$file_to" --ftp-create-dirs -k
}

# upload artifacts
upload_file()
{
  local file=$1                              # neveexec_master.0.0.9.tar.gz
  local path=$2                              # NetAct/20.0.4/INSTALL_MEDIA
  local repo_name=$3                         # artifactory-edge-uploads
  local artifactory_url=$4                   # https://10.96.170.43 
  local artifactory_credential=$5            # admin:f1qb56hrH0QndKaO01m3hNszSpmcia

  local ret=`curl -s -o /dev/null -w '%{http_code}' -u$artifactory_credential -X PUT -T "$file" "$artifactory_url/artifactory/$repo_name/$path/" --ftp-create-dirs -k`
  echo "ret: ${ret}"
  if [ "$ret" -gt 300 ] || [ "$ret" -eq 0 ] || [ "$ret" -eq 100 ]; then
    echo "fail to upload file: $file"
    exit 1
  fi
}

download_file()
{
  local file=$1
  local path=$2
  local repo_name=$3
  local artifactory_url=$4
  local artifactory_credential=$5

  local exists=$(artifact_exist "$path" "$file" "$repo_name" "$artifactory_url" "$artifactory_credential")
  if [ -z "$exists" ]; then
    echo "$file under $path does not exist, exiting..."
    exit -1
  fi
  curl -u$artifactory_credential -X GET "$artifactory_url/artifactory/$repo_name/$path/$file" -k --output "$file"
}

# get artifacts from product.txt of latest version
get_all_artifacts()
{
  artifact_json=$1

  cat "$artifact_json" | jq -r '.artifacts[]' | jq -r '.filename' | tr '\n' ',' | sed 's|,$||'
}

handle_configs_file()
{
  local new_workflow_file=$1
  local new_version=$2
  local configs_folder=$3
  local repo_name=$4
  local artifactory_url=$5
  local artifactory_credential=$6

  local file=$(basename $new_workflow_file)

  upload_file "$new_workflow_file" "NetAct/$new_version/$configs_folder" "$repo_name" "$artifactory_url" "$artifactory_credential"
#  save_artifact_to_local "$new_workflow_file" "$LOCAL_ARCHIVE_ARTIFACTS/$configs_folder"
}

handle_workflow_file()
{
  local new_workflow_file=$1
  local new_version=$2
  local repo_name=$3
  local artifactory_url=$4
  local artifactory_credential=$5

  local file=$(basename $new_workflow_file)

  sed -ri "s|VERSION_FOLDER_NEW_VERSION|$new_version|g" "$new_workflow_file"
  handle_configs_file "$new_workflow_file" "$new_version" "WORKFLOWS" "$repo_name" "$artifactory_url" "$artifactory_credential"
}

handle_deployment_file()
{
  local new_deployment_file=$1
  local new_version=$2
  local repo_name=$3
  local artifactory_url=$4
  local artifactory_credential=$5
  local file=$(basename $new_deployment_file)

  handle_configs_file "$new_deployment_file" "$new_version" "deployment" "$repo_name" "$artifactory_url" "$artifactory_credential"
}

set_proxy()
{
  export http_proxy='http://10.158.100.1:8080/'
  export https_proxy='http://10.158.100.1:8080/'
  export no_proxy='localhost,127.0.0.1,instance-data,169.254.169.254,nokia.net,.nsn-net.net,.nsn-rdnet.net,.ext.net.nokia.com,.int.net.nokia.com,.inside.nsn.com,.inside.nokiasiemensnetworks.com'
}

upload_image_to_glance()
{
  local image_name=$1
  local image_file=$2
  local openrc_file=$3

  . "$openrc_file"
  openstack image delete "$image_name" || true
  if ! glance image-create --name $image_name --disk-format qcow2 --container-format bare --progress --file "$image_file" ; then
    echo "cannot upload $image_name, exiting"
    exit 1
  fi
  rm -rf "$image_file"
}

create_vm_stack()
{
  local ndap_ip=$1
  local tool_vm_ip_id=$2

  . "$openrc_file"
  openstack stack create -t -tool-vm.hot.main.yaml -parameter-file cbam=extension.json --parameter NDAP_IP=$ndap_ip --parameter TOOL_VM_IP_ID=$tool_vm_ip_id tool_vm
}
