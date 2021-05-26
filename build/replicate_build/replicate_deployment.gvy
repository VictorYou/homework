properties([parameters([
  string(name: 'CRENDENTIALSID_TO', defaultValue: 'ndap_artifactory_admin', description: 'ndap_artifactory_admin | near_test | near_fihe3nar002'),
  string(name: 'PRODUCT_REPO_NAME_FROM', defaultValue: 'FastPass-Testing-local', description: ''),
  string(name: 'FOLDER_FROM', defaultValue: 'deployment_save_1.0.10', description: ''),
  string(name: 'NDAP_IP', defaultValue: '10.96.170.43', description: 'ndap ip')
])])

node('agent_host') {
  stage ('cleanup workspace') {
    cleanWs()
  }
  stage ('prepare variables') {
    CRENDENTIALSID_FROM = 'ca_fp_devops'
    ARTIFACTORY_FROM = 'https://esisoj70.emea.nsn-net.net:443'

    if (CRENDENTIALSID_TO == 'near_test') {
      REPO_NAME_TO = 'FastPass-Product'
      ARTIFACTORY_TO = 'https://10.74.67.37:5904'
    } else if (CRENDENTIALSID_TO == 'near_fihe3nar002') {
      REPO_NAME_TO = 'FastPass-Product'
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
    git(credentialsId: 'gitlab-viyou', branch: 'build_tvnf', url: 'git@gitlabe1.ext.net.nokia.com:fast-pass-devops/fastpass_package_deployment.git')
  }
  stage ('replicate deployment tools') {
    dir('tvnf/build/replicate_build') {
      RET = sh returnStatus: true, script: "bash replicate_deployment.sh ${PRODUCT_REPO_NAME_FROM} ${FOLDER_FROM} ${ARTIFACTORY_FROM} ${CREDENTIAL_FROM} ${REPO_NAME_TO} ${ARTIFACTORY_TO} ${CREDENTIAL_TO}"
      RET = RET.toInteger()
      if (RET != 0) {
        error "fail in stage: ${STAGE_NAME}"
      }
    }
  }
  if ("${CRENDENTIALSID_TO}" == 'ndap_artifactory_admin') {
    stage ('copy to ndap FastPass-Product') {
      jfrog_uri_parent = "https://${NDAP_IP}/artifactory/"
      data = '\'items.find({"repo":{"$eq":"FastPass-Product"}, "name":{"$eq":"NAME"}, "type":{"$eq":"folder"}}).include("*")\''
      data = data.replaceFirst('NAME', 'NetAct')
      FOLDER_NUMBER = sh returnStdout: true, script: "curl -s -k --noproxy '*' -u${CREDENTIAL_TO} --header 'content-type: text/plain' --data ${data} ${jfrog_uri_parent}api/search/aql | jq -r '.range' | jq -r '.total' "
      FOLDER_NUMBER = "${FOLDER_NUMBER}".trim().toInteger()
      echo "FOLDER_NUMBER: ${FOLDER_NUMBER}"
      if (FOLDER_NUMBER == 0) {
        copy_uri2 = "${jfrog_uri_parent}api/copy/artifactory-edge-uploads/NetAct/deployment?to=/FastPass-Product/NetAct/deployment"
      } else if (FOLDER_NUMBER == 1) {
        copy_uri2 = "${jfrog_uri_parent}api/copy/artifactory-edge-uploads/NetAct/deployment?to=/FastPass-Product/NetAct"
      } else {
        println("wrong folder number: ${FOLDER_NUMBER}")
      }
      echo "copy_uri2: ${copy_uri2}"
      RET = sh returnStdout: true, script: "curl -s -o /dev/null -w '%{http_code}' -k --noproxy '*' -u${CREDENTIAL_TO} -X POST ${copy_uri2}"
      RET = RET.toInteger()
      if (RET > 300) {
        error "fail in stage: ${STAGE_NAME}"
      }
    }
  }
}
