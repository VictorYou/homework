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
    dir('tvnf') {
      NEW_VERSION = sh returnStdout: true, script: "bash build/get_new_version.sh"
    } 
  }
  if (NEW_VERSION) {
    stage ('build apps') {
      dir('tvnf') {
        sshagent(['gitlab-viyou', 'gerrite-viyou']) {
          sh "bash build/build_app.sh ${NEW_VERSION} ${REGISTRY_CREDENTIAL}"
        }
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
}
