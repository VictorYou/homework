branch = 'build_tvnf_k8s'

properties([parameters([
  string(defaultValue: 'no', description: '(yes/no)', name: 'UPDATE_NEVE_IMAGE'), 
  string(defaultValue: 'esisoj70', description: '(near/esisoj70)', name: 'ARTIFACTORY'), 
  string(defaultValue: '10.96.170.43', description: 'ndap ip', name: 'NDAP_IP')
])])

node('agent_host') {
  stage ('cleanup workspace') {
    cleanWs()
  }
  stage ('prepare variables') {
    if (ARTIFACTORY == 'esisoj70') {
      CRENDENTIALSID = 'ca_fp_devops'
      REPO_NAME = 'FastPass-Testing-local'
      ARTIFACTORY_URL = 'https://esisoj70.emea.nsn-net.net:443'
    } else {
      error "unknown artifactory: ${ARTIFACTORY}"
    }
    withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID}", passwordVariable: 'TOKEN', usernameVariable: 'USERNAME')]) {
      ARTIFACTORY_CREDENTIAL = "${USERNAME}:${TOKEN}"
    }
    withCredentials([usernamePassword(credentialsId: "fastpass_docker_registry", passwordVariable: 'TOKEN', usernameVariable: 'USERNAME')]) {
      REGISTRY_CREDENTIAL = "${USERNAME}:${TOKEN}"
    }
    withCredentials([usernamePassword(credentialsId: "neve_docker_registry", passwordVariable: 'TOKEN', usernameVariable: 'USERNAME')]) {
      NEVE_REGISTRY_CREDENTIAL = "${USERNAME}:${TOKEN}"
    }
    echo "ARTIFACTORY_CREDENTIAL: ${ARTIFACTORY_CREDENTIAL}"
    echo "REGISTRY_CREDENTIAL: ${REGISTRY_CREDENTIAL}"
    echo "NEVE_REGISTRY_CREDENTIAL: ${NEVE_REGISTRY_CREDENTIAL}"
  }
  stage ('check out codebase and get version') {
    git(credentialsId: 'gitlab-viyou', branch: branch, url: 'git@gitlabe1.ext.net.nokia.com:fast-pass-devops/fastpass_package_deployment.git')
    dir('tvnf') {
      NEW_VERSION = sh returnStdout: true, script: "bash build/get_new_version.sh"
    } 
  }
  if (NEW_VERSION) {
    stage ('build apps') {
      dir('tvnf') {
        sshagent(['gitlab-viyou', 'gerrite-viyou']) {
          sh "bash build/build_app.sh ${NEW_VERSION} ${REPO_NAME} ${ARTIFACTORY_URL} ${ARTIFACTORY_CREDENTIAL} ${UPDATE_NEVE_IMAGE} ${NEVE_REGISTRY_CREDENTIAL} ${REGISTRY_CREDENTIAL}"
        }
      }
    }
    stage ('build configs') {
      dir('tvnf') {
        sh "bash build/build_configs.sh ${NEW_VERSION} ${REPO_NAME} ${ARTIFACTORY_URL} ${ARTIFACTORY_CREDENTIAL}"
      }
    }
  } else {
    error "error getting new version, exiting..."
  }
  stage ('tag & push to origin') {
    sshagent(['gitlab-viyou']) {
      sh "git tag homework.${NEW_VERSION} HEAD"
      sh "git push origin HEAD:${branch} --tags"
    }
  }
  stage ('cleanup workspace') {
    cleanWs disableDeferredWipeout: true, deleteDirs: true
  }
  stage ('replicate build to ndap') {
    build job: 'replicate_tvnf_k8s', parameters:[ string("name": "CRENDENTIALSID_TO", value: "ndap_artifactory_admin"),  string(name: "NDAP_IP", value: "${NDAP_IP}")]
  }
}
