properties([parameters([
  string(name: 'CRENDENTIALSID_TO', defaultValue: 'ndap_artifactory_admin', description: 'ndap_artifactory_admin | near_test | near_fihe3nar002'),
  string(name: 'NDAP_IP', defaultValue: '10.96.170.43', description: 'ndap ip')
])])

node('agent_host') {
  stage ('cleanup workspace') {
    cleanWs()
  }
  stage ('prepare variables') {
    CRENDENTIALSID_FROM = 'ca_fp_devops'
    TEST_REPO_NAME_FROM = 'FastPass-Testing-local'
    ARTIFACTORY_FROM = 'https://esisoj70.emea.nsn-net.net:443'

    if (CRENDENTIALSID_TO == 'near_test') {
      REPO_NAME_TO = 'FastPass-Testing'
      ARTIFACTORY_TO = 'https://10.74.67.37:5904'
    } else if (CRENDENTIALSID_TO == 'near_fihe3nar002') {
      REPO_NAME_TO = 'FastPass-Testing'
      ARTIFACTORY_TO = "https://fihe3nar002.emea.nsn-net.net"
    } else if (CRENDENTIALSID_TO == 'ndap_artifactory_admin') {
      REPO_NAME_TO = 'artifactory-edge-uploads'
      ARTIFACTORY_TO = "https://${NDAP_IP}"
    } else {
      error "invalid credential id: ${CRENDENTIALSID_TO}"
    }
    CREDENTIAL_FROM = ""
    CREDENTIAL_TO = ""
    withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_FROM}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
      CREDENTIAL_FROM = "${GLOBAL_ARTIFACTORY_USERNAME}:${GLOBAL_ARTIFACTORY_TOKEN}"
    }
    withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_TO}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
      CREDENTIAL_TO = "${GLOBAL_ARTIFACTORY_USERNAME}:${GLOBAL_ARTIFACTORY_TOKEN}"
    }
  }
  stage ('check out codebase') {
    git(credentialsId: 'gitlab-viyou', branch: 'build_tvnf_k8s', url: 'git@gitlabe1.ext.net.nokia.com:fast-pass-devops/fastpass_package_deployment.git')
  }
  stage ('get latest version') {
    dir('tvnf/build') {
      LATEST_VERSION = sh returnStdout: true, script: ''' 
        bash get_latest_version_from_git.sh
      '''
      echo "${LATEST_VERSION}"
    }
  }
  stage ('replicate latest build') {
    dir('tvnf/build/replicate_build') {
      RET = sh returnStatus: true, script: "bash replicate_tvnf.sh ${TEST_REPO_NAME_FROM} ${ARTIFACTORY_FROM} ${CREDENTIAL_FROM} ${REPO_NAME_TO} ${ARTIFACTORY_TO} ${CREDENTIAL_TO}"
    }
  }
  if ("${CRENDENTIALSID_TO}" == 'ndap_artifactory_admin') {
    stage ('copy to ndap FastPass-Testing') {
      jfrog_uri_parent = "https://${NDAP_IP}/artifactory/"
      data = '\'items.find({"repo":{"$eq":"FastPass-Testing"}, "name":{"$eq":"NAME"}, "type":{"$eq":"folder"}}).include("*")\''
      data = data.replaceFirst('NAME', 'NetAct')
      FOLDER_EXIST = sh returnStdout: true, script: "curl -s -k --proxy 10.144.1.10:8080 -u${CREDENTIAL_TO} --header 'content-type: text/plain' --data ${data} ${jfrog_uri_parent}api/search/aql | jq -r '.range' | jq -r '.total' "
      FOLDER_EXIST = "${FOLDER_EXIST}".trim()
      echo "FOLDER_EXIST: ${FOLDER_EXIST}"
      if (FOLDER_EXIST == '0') {
        copy_uri1 = "${jfrog_uri_parent}api/copy/artifactory-edge-uploads/NetAct/${LATEST_VERSION}?to=/FastPass-Testing/NetAct/${LATEST_VERSION}"
      } else {
        copy_uri1 = "${jfrog_uri_parent}api/copy/artifactory-edge-uploads/NetAct/${LATEST_VERSION}?to=/FastPass-Testing/NetAct/"
      }
      echo "copy_uri1: ${copy_uri1}"
      sh "curl -k --proxy 10.144.1.10:8080 -u${CREDENTIAL_TO} -X POST ${copy_uri1}"
    }
    stage ('integrity check') {
      jenkins_uri_parent = "https://${NDAP_IP}/jenkins/"
      build_job_uri = "${jenkins_uri_parent}job/artifact_integrity_check/build"
      parameters = "--data-urlencode json='{'parameter': [{'name': \"ARTIFACT_PATH\", 'value': \"FastPass-Testing/NetAct/${LATEST_VERSION}/METADATA/product.txt\"}]}'"
      withCredentials([usernamePassword(credentialsId: "ndap_jenkins_admin", passwordVariable: 'ndap_jenkins_token', usernameVariable: 'ndap_jenkins_user')]) {
        sh "curl -f -k --proxy 10.144.1.10:8080 -u${ndap_jenkins_user}:${ndap_jenkins_token} -X POST ${build_job_uri} ${parameters}"
      }
    }
  }
  stage ('check build status') {
    if (RET != 0) {
      currentBuild.result = 'FAILURE'
    }
  }
}
