properties([parameters([string(defaultValue: 'esisoj70', description: '(near/esisoj70)', name: 'ARTIFACTORY_FROM'),  string(defaultValue: 'near', description: '(near/esisoj70)', name: 'ARTIFACTORY_TO')])])
node('agent_host') {
  stage ('cleanup workspace') {
    cleanWs()
    if (ARTIFACTORY_FROM == 'esisoj70') {
      CRENDENTIALSID_FROM = 'ca_fp_devops'
    } else {
      CRENDENTIALSID_FROM = 'netactadmin'
    }
    if (ARTIFACTORY_TO == 'near') {
      CRENDENTIALSID_TO = 'netactadmin'
    } else {
      CRENDENTIALSID_TO = 'ca_fp_devops'
    }
  }
  stage ('check out codebase') {
    git(credentialsId: 'gitlab-viyou', branch: 'build_tvnf', url: 'git@gitlabe1.ext.net.nokia.com:fast-pass-devops/fastpass_package_deployment.git')
    ARTIFACTS_TXT_FROM ='artifact_list_from.txt'
    ARTIFACTS_TXT_TO ='artifact_list_to.txt'
  }
  stage ('get artifacts for building app image') {
    withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_FROM}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
      dir('tvnf/build/replicate_artifact') {
        ARTIFACTS_APP_FROM = sh returnStdout: true, script: "bash get_artifacts_app.sh ${ARTIFACTORY_FROM} ${ARTIFACTS_TXT_FROM}"
        echo "ARTIFACTS_APP_FROM: ${ARTIFACTS_APP_FROM}"
      }
    }
    withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_TO}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
      dir('tvnf/build/replicate_artifact') {
        ARTIFACTS_APP_TO = sh returnStdout: true, script: "bash get_artifacts_app.sh ${ARTIFACTORY_TO} ${ARTIFACTS_TXT_FROM}"
        echo "ARTIFACTS_APP_TO: ${ARTIFACTS_APP_TO}"
      }
    }
  }
  if (ARTIFACTS_APP_FROM == ARTIFACTS_APP_TO) {
    echo "no need to replicate artifacts for building app"
    RET = 0
  } else {
    stage ('download artifacts for app from') {
      withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_FROM}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
        dir('tvnf/build/replicate_artifact') {
          RET = sh returnStatus: true, script: "bash download_artifacts_app.sh ${ARTIFACTORY_FROM} ${ARTIFACTS_APP_FROM} ${ARTIFACTS_APP_TO}"
          echo "RET download artifact from: ${RET}"
        }
      }
    }
    stage ('upload artifacts for app to') {
      withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_TO}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
        dir('tvnf/build/replicate_artifact') {
          RET = sh returnStatus: true, script: "bash upload_artifact_list.sh ${ARTIFACTORY_TO} ${ARTIFACTS_TXT_FROM}"
          echo "RET upload artifact_list.txt to: ${RET}"
          if (RET == 0) {
            RET = sh returnStatus: true, script: "bash build/replicate_artifact_upload_artifacts_app.sh ${ARTIFACTORY_TO} ${ARTIFACTS_APP_FROM} ${ARTIFACTS_APP_TO}"
            echo "RET upload artifact to: ${RET}"
          }
        }
      }
    }
  } 
  stage ('get other artifacts') {
    dir('tvnf/build/replicate_artifact') {
      withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_FROM}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
        ARTIFACTS_OTHERS_FROM = sh returnStdout: true, script: "bash get_artifacts_others_from.sh ${ARTIFACTORY_FROM}"
        echo "ARTIFACTS_OTHERS_FROM: ${ARTIFACTS_OTHERS_FROM}"
      }
      withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_TO}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
        ARTIFACTS_OTHERS_TO = sh returnStdout: true, script: "bash get_artifacts_others_to.sh ${ARTIFACTORY_TO} ${ARTIFACTS_OTHERS_FROM}"
        echo "ARTIFACTS_OTHERS_TO ${ARTIFACTS_OTHERS_TO}"
      }
      if (ARTIFACTS_OTHERS_TO == '') {
        echo "no need to replicate, exiting"
        RET = 0
      } else {
        withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_FROM}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
          RET = sh returnStatus: true, script: "bash download_artifacts_others.sh ${ARTIFACTORY_FROM} ${ARTIFACTS_OTHERS_TO}"
          echo "RET download other artifacts from: ${RET}"
        }
        if (RET == 0) {
          withCredentials([usernamePassword(credentialsId: "${CRENDENTIALSID_TO}", passwordVariable: 'GLOBAL_ARTIFACTORY_TOKEN', usernameVariable: 'GLOBAL_ARTIFACTORY_USERNAME')]) {
            RET = sh returnStatus: true, script: "bash upload_artifacts_others.sh ${ARTIFACTORY_TO} ${ARTIFACTS_OTHERS_TO}"
            echo "RET upload other artifacts to: ${RET}"
          }
        }
      }
    }
  }
  stage ('check build status') {
    if (RET != 0) {
      currentBuild.result = 'FAILURE'
    }
  }
  stage ('cleanup workspace') {
    cleanWs disableDeferredWipeout: true, deleteDirs: true
  }
}
