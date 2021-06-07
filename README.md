# Overview
This homework deploys a dummy app to eks, and when you curl it, it should return OK.
```hcl
curl -f -k -X POST https://homework-app.ddns.net:30036/testvnf/v1/connectTests/123456          # {"result":"OK"}
```
To deploy the app, you can build https://homework-jenkins.ddns.net:30036/job/deploy_app/

To undeploy the app, you can build https://homework-jenkins.ddns.net:30036/job/undeploy_app/

If you update the codebase, and would like to build a new docker image for the app, you can build https://homework-jenkins.ddns.net:30036/job/build_app/
# Deployment
Below are the steps to set up necessary tooling and deploy app.
## Prepare eks
* clone codebase and checkout master branch
```hcl
git clone https://github.com/VictorYou/homework.git
cd homework
git checkout master
```
* deploy eks
```hcl
cd deploy/eks
terraform init
terraform apply -var-file="testing.tfvars" -var="access_key=<your access key>" -var="secret_key=<your secret key>"
mv kubeconfig_test-eks-LumdwL5J kubeconfig_test-eks
```
this may take 10 ~ 15 minutes.
* set up local command environment
```hcl
alias eh='/snap/bin/helm --kubeconfig <codebase folder>/deploy/eks/kubeconfig_test-eks'
alias ek='kubectl --kubeconfig <codebase folder>/deploy/eks/kubeconfig_test-eks'
alias ekh='kubectl --kubeconfig <codebase folder>/deploy/eks/kubeconfig_test-eks --namespace homework'
```
* verify eks is up
```hcl
ek get no
```
### deploy ingress controller
ingress controller routes requests to app service.
```hcl
eh repo add bitnami https://charts.bitnami.com/bitnami
eh install my-ingress-controller bitnami/nginx-ingress-controller
```
* check port for ingress controller
```hcl
ek get svc my-ingress-controller-nginx-ingress-controller
```
In this case, it is `30537/TCP` for http and `30036/TCP` for https in this case. From aws console，edit security group to allow TCP traffic for those 2 ports.
## Prepare jenkins
### prepare jenkins image
This image is based on `jenkins/kenkins`, with a bunch of plugins, docker and helm installed, so that we can trigger pipeline and build docker image from jenkins pod.
```hcl
cd jenkins
docker build -t viyou/jenkins:0.7 .
docker tag viyou/jenkins:0.7 viyou/jenkins:latest
docker push
```
### deploy jenkins and setup
* deploy jenkins and get password
```hcl
cd jenkins/jenkins
eh install myjenkins . --set controller.image="viyou/jenkins" --set controller.tag=latest --set controller.installPlugins=false
ek exec -it svc/myjenkins -c jenkins -- /bin/cat /run/secrets/chart-admin-password && echo
```
password is `UmPnUvrbluoku2Np37um36` in this case.
* deploy ingress for jenkins

Ingress configures the rules for ingress controller to route requests.
```hcl
ek apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jenkins-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: "homework-jenkins.ddns.net"
    http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: myjenkins
            port:
              number: 8080
EOF
```
wait for 1 minute or 2 and check ingress is effective.
```hcl
ek get ing jenkins-ingress    # jenkins-ingress   <none>   homework-jenkins.ddns.net   54.151.84.97   80      10h
```
Apply for dynamic dns from https://my.noip.com, with hostname as `homework-jenkins.ddns.net` and `homework-app.ddns.net` and ip as what you get from checking ing, i.e, `54.151.84.97`, in this case.
* configure build from jenkins

In order to build docker image from jenkins pod, change permission on all nodes, in this case:
```hcl
ssh -i "homework.pem" ec2-user@ec2-54-151-84-97.us-west-1.compute.amazonaws.com "sudo chmod 777 /var/run/docker.sock"
ssh -i "homework.pem" ec2-user@ec2-13-57-10-17.us-west-1.compute.amazonaws.com "sudo chmod 777 /var/run/docker.sock"
ssh -i "homework.pem" ec2-user@ec2-54-215-192-233.us-west-1.compute.amazonaws.com "sudo chmod 777 /var/run/docker.sock"
```
Open browser and access jenkins: https://homework-jenkins.ddns.net:30036 .

Create credentials to access github and dockerhub, `github-viyou` and `dockerhub-viyou` in this case.

Create a job to build app: https://homework-jenkins.ddns.net:30036/job/build_app/ .
## Prepare resources for app
This will create secret, role, rolebinding for deploying app in this namespace.
```hcl
cd deploy/app
ek create ns homework
terraform apply
```
Find a preferred node with enough resources, and label it, in this case:
```hcl
k label no ip-10-0-4-146.us-west-1.compute.internal role=app
```
Create a jenkins job to deploy and undeploy the app, namely, https://homework-jenkins.ddns.net:30036/job/deploy_app/ and https://homework-jenkins.ddns.net:30036/job/undeploy_app/ respectively.
Check encrypted `ca.crt` and `token` for helm to access homework resources:
```hcl
ekh get secret                                               # app-token-s5c5l       kubernetes.io/service-account-token   3      2d20h
ekh get secret app-token-s5c5l -o jsonpath='{.data.ca\.crt}'
ekh get secret app-token-s5c5l -o jsonpath='{.data.token}'
```
## Deploy app
Use the encrypted `ca.crt` and `token` as parameters to build https://homework-jenkins.ddns.net:30036/job/deploy_app/, `k8s_endpoint` can be checked from file `deploy/eks/kubeconfig_test-eks`, i.e, `https://773EF95D5147AA9EE79774ED29B85923.gr7.us-west-1.eks.amazonaws.com` in this case.
Then try accessing app with curl.
```hcl
curl -f -k -X POST https://homework-app.ddns.net:30036/testvnf/v1/connectTests/123456          # {"result":"OK"}
```
and if you undeploy app with https://homework-jenkins.ddns.net:30036/job/undeploy_app/, it should fail.
```hcl
curl -f -k -X POST https://homework-app.ddns.net:30036/testvnf/v1/connectTests/123456          # curl: (22) The requested URL returned error: 404 
```
