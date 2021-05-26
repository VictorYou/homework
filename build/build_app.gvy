branch = 'master'

properties([parameters([
  string(defaultValue: 'no', description: '(yes/no)', name: 'UPDATE_NEVE_IMAGE'), 
])])

node('agent_host') {
  stage ('cleanup workspace') {
    cleanWs()
  }
  stage ('prepare variables') {
    withCredentials([usernamePassword(credentialsId: "dockerhub-viyou", passwordVariable: 'TOKEN', usernameVariable: 'USERNAME')]) {
      REGISTRY_CREDENTIAL = "${USERNAME}:${TOKEN}"
    }
    echo "REGISTRY_CREDENTIAL: ${REGISTRY_CREDENTIAL}"
  }
  stage ('check out codebase and get version') {
    git(credentialsId: 'github-viyou', branch: branch, url: 'https://github.com/VictorYou/homework.git')
    dir('build') {
      NEW_VERSION = sh returnStdout: true, script: "bash get_new_version.sh"
    } 
  }
  if (NEW_VERSION) {
    stage ('build apps') {
      dir('build') {
        sshagent(['github-viyou', 'gerrite-viyou']) {
          sh "bash -ex build_app.sh ${NEW_VERSION} ${REGISTRY_CREDENTIAL}"
        }
      }
    }
  } else {
    error "error getting new version, exiting..."
  }
  stage ('tag & push to origin') {
    sshagent(['github-viyou']) {
      sh "git tag homework.${NEW_VERSION} HEAD"
      sh "expect build/push_code"
    }
  }
  stage ('cleanup workspace') {
    cleanWs disableDeferredWipeout: true, deleteDirs: true
  }
}
