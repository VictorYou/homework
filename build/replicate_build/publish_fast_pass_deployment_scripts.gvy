node {
  stage ('cleanup workspace') {
    cleanWs()
  }
  stage ('check out codebase') {
    git(credentialsId: 'gitlab-viyou', branch: 'master', url: 'https://gitlabe1.ext.net.nokia.com/fast-pass-devops/fastpass_package_scripts')
  }
  stage ('publish scripts') {
    sh "python3 publish_deploy_scripts.py --targetRepo=${repo_target} --apikey=${api_key} --release=${BUILD_ID} --swVersionItem=${sw_version_item} --euECCN=${eu_eccn_code} --usECCN=${us_eccn_code}" 
  }
}