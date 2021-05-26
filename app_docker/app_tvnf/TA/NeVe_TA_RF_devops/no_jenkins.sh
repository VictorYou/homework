#!/bin/bash

#export LAB=clab3417
#export NE_NAME=LTESUPERMAN
#export TAGS='ADAPTATION_MANAGER&CRITICAL&WEBAPP,AOM&CRITICAL&WEBAPP'
#export SESSION_ID=325ff5c1-d10f-49da-9533-4fbd90acc624
#export FOLDER=level3
#export Browser=Firefox


### create LAB variable ###
if [[ ${LAB:0:8} == sprin* ]] ; then
  LAB=LAB${LAB:9}
else
  LAB=CLAB${LAB:4}
fi
echo "NEW_LAB=$LAB"
 
### create TEST_FILE variable ###
if [ -n "$TEST_FILE" ] ; then
  FILE=$TEST_FILE.tsv
fi
echo "FILE=$FILE"
 
### create tag variable ###
#NE_TYPE=${ELEMENT_NAME%-*}
#echo "NE_TYPE=$NE_TYPE"
 
#tags include = tag&NE_TYPE
result=''
while [ ! -z "$TAGS" ]; do
  tag=$(echo $TAGS | sed -r '/,/!d')
  if [ -z "$tag" ]; then
    tag=$TAGS
    TAGS=''
  else  
    tag=$(echo $TAGS | sed -r 's|([^,]*),(.*)|\1|')
    TAGS=${TAGS#$tag,}
  fi  
  result=$result" -i $tag"
done

export JRV_TESTTAG="${result,,}"
 
 
### convert element type and name to lowercase ###
 
echo "LOWER_ELEMENT_NAME=`echo ${ELEMENT_NAME,,} | awk -F '-' '{print $2}'`"
 
### create REDUCE_LOGS variable ###
 
if [ "$REDUCE_LOGS" = "Yes" ] ; then
  echo "JRV_REDUCE_LOGS="TRUE""
fi
 
### create LOGLEVEL_DEBUG variable ###
 
if [ "$LOGLEVEL_DEBUG" = "Yes" ] ; then
  echo "JRV_LOGLEVEL_DEBUG="TRUE""
fi
 
### Create JRV_DOCKER_ variables ###
#echo "NODE NAME=`echo ${NODE_NAME}`"
#JRV_DOCKER_HOSTNAME=`echo ${NODE_NAME} |  sed 's/.*-//'`
 #echo "JRV_DOCKER_HOSTNAME=`echo ${JRV_DOCKER_HOSTNAME}`"
export JRV_DOCKER_HOSTIP=`hostname -i`
echo "JRV_DOCKER_HOSTIP=`echo ${JRV_DOCKER_HOSTIP}`"
 
### Ugly fix for custom hosts that should be added to /etc/hosts file after docker startup ###
#sudo /root/etchosts.sh import /root/customhosts --append

### USER CONFIG ###
 
# e.g. LAB123
export JRV_LAB_UNDER_TEST=$LAB
export JRV_ELEMENT_UNDER_TEST=$NE_NAME
 
# e.g. "-i LEVEL2" or "-i LEVEL6 -e FM" or "-i LEVEL2 -i LEVEL3" without ""
# Delete or comment this line if you don't need tags
#e.g. JRV_TESTTAG=-i INTEGRATE_NE&LTE_OMS
#JRV_TESTTAG=-i INTEGRATE_NE&LTE_OMS_NEIW -e NEVE&NEAC
#JRV_TESTTAG="$JRV_TESTTAG -L TRACE"
 
# e.g. tests/level6/ or /tests/level2/tc_check_core_files_in_nas.tsv
 
## VARIABLES ###
# Don't touch these #
export WORKSPACE="/tmp/workspace"
mkdir -p "$WORKSPACE"
chmod 777 "$WORKSPACE"
export JRV_TESTPATH="robot/tests/$FOLDER"
export JENKINS_OUTPUTDIR="/tmp/logs/${SESSION_ID}/output"   # /tmp/logs/1f00-267-02--tc-open-and-Lau/output
mkdir -p "$JENKINS_OUTPUTDIR"
#chmod 777 "$JENKINS_OUTPUTDIR"
export JRV_ROBOT_OPTIONS="--outputdir $JENKINS_OUTPUTDIR"


###################### BUILD BEGINS ##########################
cd $WORKSPACE
rm -rf *
sudo find /home/tauser/NeVe_TA_RF  -maxdepth 1 -mindepth 1 -exec cp -r {} $WORKSPACE \;
sudo find $WORKSPACE -exec chown tauser:tauser {} \;
find $WORKSPACE -type f -exec dos2unix -q {} \;

export HOME=/home/tauser
export USER=tauser

bash -x "$WORKSPACE/configuration/nevescripts/run_docker.sh"
echo "test finished: $?"

