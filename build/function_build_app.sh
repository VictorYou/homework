#!/bin/bash -ex

CURRENTDIR=$(dirname $0)

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

# get new version
get_next_version()
{
  local version=$1
  version_tail=${version##*.}
  version_head=${version%${version_tail}}
  version_tail=$((version_tail+1))
  echo $version_head$version_tail
}
