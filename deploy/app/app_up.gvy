properties([parameters([
  string(name: 'app_name', defaultValue: 'app'),
  string(name: 'app_host', defaultValue: 'homework-app.ddns.net'),
  string(name: 'app_port', defaultValue: '30036'),
  string(name: 'app_docker_image', defaultValue: 'viyou/app_docker:latest'),
  string(name: 'app_version', defaultValue: '0.0.1'),
  string(name: 'k8s_endpoint', defaultValue: 'https://773EF95D5147AA9EE79774ED29B85923.gr7.us-west-1.eks.amazonaws.com'),
  string(name: 'namespace', defaultValue: 'homework'),
])])

node {
  stage ('clean up workspace') {
    cleanWs()
  }
  stage ('check out codebase and get version') {
    git(credentialsId: 'github-viyou', branch: 'master', url: 'https://github.com/VictorYou/homework.git')
    dir('build') {
      NEW_VERSION = sh returnStdout: true, script: "bash get_new_version.sh"
    }
  }
  stage('prepare variables') {
//    app_docker_image = app_docker_image_name + '/' + app_version
    k8s_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjB5bDZ0dUlJT3F6cVBnWnlRUjNDUmtob0ZpazBmZzVHX3FTb1pkNG84dm8ifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJmYXN0cGFzcy10dm5mIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InR2bmYtdG9rZW4tNHp4NDYiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoidHZuZiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjgwZDNkMDdkLTIyZmQtNGQzNi05MTFiLTFkNTliMmNiNWY3MSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpmYXN0cGFzcy10dm5mOnR2bmYifQ.Adah0x9aL_lEBoAd4I-3n5oSU888mYxQpQvEgYb3i-I5w1ZVwnSrYAWea0fSpfN3Mupj-XbyLz7pL37dJ-Eq542uSz6WJIgxqbyFV5uiMYvKoEwDFK6wmmftm1gm8mgmvwgjLuCk_MIrZmtK_WmLCcs1i9ctunz1J7VVPcfvqUp6n40MP8tG5vgZZfBe8cBVk5jdxTtsg7FN4mWxTSnGaNAJEHhN8-SM6kJLeHoigLjmSL6-KD1Z5ZqEuf2q90B426eUZE-YH3mS5pAYY_SClezgf4jYdJX79b6GtVDHYD1Nmo5DrI6WWMGBRUO4yOPXVksVZKEQkuVWH9t5aX7caw'
    certificate = 'LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUVPekNDQXlPZ0F3SUJBZ0lVSGhKMTNlTWxYbzFrNWNjSmdJaGlnMGN6N0o0d0RRWUpLb1pJaHZjTkFRRUwKQlFBd1BERTZNRGdHQTFVRUF4TXhUbTlyYVdFZ1JHVjJiM0J6SUVGMWRHOXRZWFJwYjI0Z1VHeGhkR1p2Y20wZwpRMEVnTFNBME5XRkZNRm80V21OT05qQWVGdzB5TVRBMU1qY3dPVEUwTURkYUZ3MHlNakExTWpjd09URTBNemRhCk1Da3hKekFsQmdOVkJBTVRIbVpoYzNSd1lYTnpMWFIyYm1ZeExuUjJibVl1Ym1SaGNDNXNiMk5oYkRDQ0FTSXcKRFFZSktvWklodmNOQVFFQkJRQURnZ0VQQURDQ0FRb0NnZ0VCQU9qZ2FpVmd2cS9HMWdadXpVNHlqODBPUndGdwp4eWJJeUMwZnRzaWMwQUFGSkZ1RHIxeERHMkxqUnA0ekdZYnhIZi9XU3VpREl1SHJoRXJKTFJsNGJadW4vNTFMCisvQURpNXE4RWp4ZmMvMExieTJKRnV1N2I0ZGJxNU5WdDJrSUtESkJLdkV1MEIranFMbXpOemVvbDFnNy9VcjgKS0FUTnNLdkwzckJEY2hXVXc0ODZzZk9aeTA4cjBPUDFjQlpycmpDT3J1SUFucWo1dzFMcWh6NlNmVmFOUHp5TgpNcmVVU2kvbDdLOHBtT2QwQU5tVGRNNy85WFRaaVhxbDhVUzlHUDl2b2YySjNUb2FwdHpYenp6NlVrUzhGaEZnCjQ1TjJ3dFE5RzRLZnZQOXJlTHY3TWlBWHNmZHZVNEoyYkhtZU10OW41bnc1aWF0QUdZUm03Zjl5ODZNQ0F3RUEKQWFPQ0FVWXdnZ0ZDTUE0R0ExVWREd0VCL3dRRUF3SURxREFkQmdOVkhTVUVGakFVQmdnckJnRUZCUWNEQVFZSQpLd1lCQlFVSEF3SXdIUVlEVlIwT0JCWUVGRVlNbEtDUzYwbWY2ZVU1amo2cnh5QVBiVjFpTUI4R0ExVWRJd1FZCk1CYUFGTlpmZzhEeWVFMi9vcElvTmhWL2w2VjBpb0taTUZjR0NDc0dBUVVGQndFQkJFc3dTVEJIQmdnckJnRUYKQlFjd0FvWTdhSFIwY0hNNkx5OXVaR0Z3TFhaaGRXeDBMbVJsWm1GMWJIUXVjM1pqTG1Oc2RYTjBaWEl1Ykc5agpZV3c2T0RJd01DOTJNUzl3YTJrdlkyRXdLUVlEVlIwUkJDSXdJSUllWm1GemRIQmhjM010ZEhadVpqRXVkSFp1ClppNXVaR0Z3TG14dlkyRnNNRTBHQTFVZEh3UkdNRVF3UXFCQW9ENkdQR2gwZEhCek9pOHZibVJoY0MxMllYVnMKZEM1a1pXWmhkV3gwTG5OMll5NWpiSFZ6ZEdWeUxteHZZMkZzT2pneU1EQXZkakV2Y0d0cEwyTnliREFOQmdrcQpoa2lHOXcwQkFRc0ZBQU9DQVFFQUsyYkZpNzFuTWQ5OXluRWxyQldHMFM3WTRsbWEvWXgrZXNLZlRRKzNDWkdVCnVablVWSGdqci9FVWpwcnhubWhUem5tYmgxclR4b2VoZnRnQ25HRmdjQWFoY3N4azdWVlpsRkhQeFdNUjRHUEMKRTh4OHlSTVJodUNOUnhUblFja3Q5bVFqR3VMc0ZZVGRWdWJKelNRUjZCZ0RudWlGMjNObFRTdFNLV1FyZWsyOQpSRUcxZGcxU0J3dGMwTkw4aEp0S3c0ZnlSenlMR0psOU1YNE5WdjNRcnF0ZUpYRFd6YXVDUzNHMzdTSncwVnZwCjJBcDdlTmt4VnR0T1VHTk91cmZHc01DUnlyTHFBd2VYT28zQU0vbDlKMzR1L2N0dU13VUVqTVRHK0tHY3FWbisKZXJublBNcEVkSWFxYmJaRWJPZVFSdWRuc2JWQkpQdk5XeXpBMC95d0tBPT0KLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQ==' 
    private_key = 'LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFcFFJQkFBS0NBUUVBNk9CcUpXQytyOGJXQm03TlRqS1B6UTVIQVhESEpzaklMUisyeUp6UUFBVWtXNE92ClhFTWJZdU5HbmpNWmh2RWQvOVpLNklNaTRldUVTc2t0R1hodG02Zi9uVXY3OEFPTG1yd1NQRjl6L1F0dkxZa1cKNjd0dmgxdXJrMVczYVFnb01rRXE4UzdRSDZPb3ViTTNONmlYV0R2OVN2d29CTTJ3cTh2ZXNFTnlGWlREanpxeAo4NW5MVHl2UTQvVndGbXV1TUk2dTRnQ2VxUG5EVXVxSFBwSjlWbzAvUEkweXQ1UktMK1hzcnltWTUzUUEyWk4wCnp2LzFkTm1KZXFYeFJMMFkvMitoL1luZE9ocW0zTmZQUFBwU1JMd1dFV0RqazNiQzFEMGJncCs4LzJ0NHUvc3kKSUJleDkyOVRnblpzZVo0eTMyZm1mRG1KcTBBWmhHYnQvM0x6b3dJREFRQUJBb0lCQVFEYTlGMTQ1VnlFd3N2cQo0blVRYUFQQ3hnREcvdldRcHNsbmUrRU5BRHVsT1RCMUJ2eHpIL2w0NGI0ODhraTNFcStsSXlQdE41Y3RtWllhCkJzcnJuc3BYeHY1VU0rUWVTQWNUcG03eTZzQ1FsQmFsVnJjQlQ0dE9Wa2VjME1RUThnVnhNc3FnVithQlNReFUKQllnT1FlcUNvR3pIK3d2WmNGZ0RQejBTdDJkbGwxMXNsWVB6YnZSWWVtbUtSY1Nxb05oYmtCVGs3QVdEdkFXYwpiZW5BQVl0MW80aSs1SmxPR3ZBUERQRDZwRXBhb3lVdW9nQUppY1VjVVc4REpXSjhITC9NNy8rS0JaZFVoMkFtCitCc2lkYy9LOUZDQzlTcmxqVUc0VndBT210cEtBdmhLRndZR0JidlRqbTM3Vy9LR1RBZ2dsVnNwbVhXVHRSUzIKOHhublNOTDVBb0dCQU8wYnM5dldNZ3ZZelBVZzN1L08zanhTVkNTTndiRStzZFBqODZLdXhHc1YwVnZ2VU9qUApWejhhTGc1R3hjMVRnUDVTREF0dTF1ZUtINlFjSkdHdytQZ3lNYnRCRkpwWlVZY0E4ZkRCbExpYXVHNWJuWXJnCjRuRmgrMGxtdTMrdkVjMmhzQTRSSmNteWxicWNuVWJWc0JZODNPTU5ZcW1KeXFSdlJmOGFaSFp2QW9HQkFQdHUKWm5VbytOSnVLWUZtMFdQanhTL0dqZHpEanpJbU5kMmJ4d3RCOXI4bkRPcTVZSmxJQlZpM2tEblBWSmtNNlZPTApWNUs5aVBPUmUrQVM1MlFGMm9XR3VBd3hrUHFoTmFmSldkT2VvTGJucDdORFFhQUE1WG4xaWM0aGFkRkVSN3BMCnNzSmplWVZyRVJablpuY0lDREZEa1ZWajVNYWtTcVNRblkvM0xoQU5Bb0dCQU5jQ2lQMnY1YUFTa0FFMU5wUlYKamZjN1hPdnMxQmpMVm14anlGbmNpMmJqMlA2NkxDK0JYWWR1VVJkSEhEV09KR242c3N0blRsK1dSQTBJTEFHZQpmcFpxeGVnZEl2YTRTaExYUzQzYnJPWWQvMktybDFnSmg2M3pnUEJWeFc4S3JXVS8ycXRXNTJKWW5DZ2x2d1V0CjMwaTdGajZhczc0em9sdXNQOWdOOGMzbkFvR0FkVkRPNTYzRlk5Slk5WEwzRW9ldGN4eFBCd29NWDVicW5VdFoKTlV5RENDLzlXK3hCUVdRVWNvKzc4TzFuaUw0NGhHM0kzOFFtQ1pnQlY4MGFRRlptM3RTOFBaeEhERnA2QVo3MgpsY0kzTlFDa0JBWEdzaFNZL2kzdUxjcnpaOXhYSjNxNG52RHhPNnA0WDU3QmRacSt6OVc2RTBDMzkyT2pIR1FKCjBLbkJ5V1VDZ1lFQWpaWjNERTJHVjlwbGk2b2ZyV2tHa1cyeW5IMEtBQ09uSzlLcDlSNE5CNkJyM3kyaTE3SC8KUHVyVkNWbUVRVnB0cmh5elhhbk9yQUQzL3ZpeEtvVnUyVGI3THpiR1U4VWN1WERCYURIODJNMjYxZGJUZkNTRApCUzh3eWtOb2pyK2djZElnY0owYjdyVHZSQXpKSmhlQTZpM3A4Q3dkeS9INlhaUWc2TGoxU293PQotLS0tLUVORCBSU0EgUFJJVkFURSBLRVktLS0tLQ=='
//    helmcmd = "/snap/bin/helm --kube-ca-file deploy/k8s_ca --kube-apiserver ${k8s_endpoint} --kube-token ${k8s_token} -n ${namespace}"
    println("namespace: ${namespace}")
//    helmcmd = "/snap/bin/helm --kubeconfig deploy/eks/kubeconfig_test-eks -n ${namespace}"
    helmcmd = "/snap/bin/helm --kubeconfig deploy/eks/kubeconfig_test-eks -n " + namespace
  }
  stage('run helm') {
    sh """
$helmcmd install ${app_name} --set certificate=${certificate} --set private_key=${private_key} --set appImage=${app_docker_image} --set appVersion=${app_version} --set appHost=${app_host} app_chart
"""
//    command = "timeout 900 bash -c 'until curl -f --cacert ${chart_folder}/ndap_ca -X POST https://${app_host}:${app_port}/testvnf/v1/connectTests/123456; do echo waiting for certificate to be effective; sleep 10; done'"
    sh """
timeout 900 bash -c "until curl --noproxy '*' -f -k -X POST https://${app_host}:${app_port}/testvnf/v1/connectTests/123456; do echo waiting for certificate to be effective; sleep 10; done"
"""
  }
}

