# homework
this homework deploys a dummy web app to eks, and when you curl it, it returns OK
```hcl
curl -f -k -X POST https://homework-app.ddns.net:30036/testvnf/v1/connectTests/123456          # {"result":"OK"}
```
## prepare eks
### clone codebase and checkout master branch
```hcl
git checkout master
```
### deploy eks
```hcl
cd deploy/eks
terraform init
terraform apply -var-file="testing.tfvars" -var="access_key=<your access key>" -var="secret_key=<your secret key>"
mv kubeconfig_test-eks-LumdwL5J kubeconfig_test-eks
```
set up local command environment
```hcl
alias eh='/snap/bin/helm --kubeconfig <codebase folder>/deploy/eks/kubeconfig_test-eks'
alias ek='kubectl --kubeconfig <codebase folder>/deploy/eks/kubeconfig_test-eks'
```
verify eks is up
```hcl
ek get no
```
### deploy ingress controller
```hcl
eh repo add bitnami https://charts.bitnami.com/bitnami
eh install my-ingress-controller bitnami/nginx-ingress-controller
```
check port for ingress controller
```hcl
ek get svc my-ingress-controller-nginx-ingress-controller
```
in this case, it is 32445/TCP for http and 32723/TCP for https in this case. modify from aws console，edit security group to allow TCP traffic for those 2 ports.
## prepare jenkins
### prepare jenkins image
```hcl
cd jenkins
docker build -t viyou/jenkins:0.0 .
docker tag viyou/jenkins:0.0 viyou/jenkins:latest
docker push
```
### deploy jenkins and setup
deploy jenkins and get password
```hcl
cd jenkins/jenkins
eh install myjenkins . --set controller.image="viyou/jenkins" --set controller.tag=latest --set controller.installPlugins=false
ek exec -it svc/myjenkins -c jenkins -- /bin/cat /run/secrets/chart-admin-password && echo
```
password is 66q6LlUXJbCf1EV8IlyjFz in this case.
apply for dynamic jenkins from https://my.noip.com, with hostname as homework-jenkins.ddns.net and homework-app.ddns.net and ip as what you get from checking ing, i.e, 13.57.13.46, in this case
deploy ingress for jenkins
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
wait for 1 minute or 2 and check ingress is effective
```hcl
ek get ing
```
open browser and access jenkins: https://homework-jenkins.ddns.net:30036
in order to build docker image from jenkins pod, change permission on all nodes, eg:
```hcl
ssh -i "homework.pem" ec2-user@ec2-13-57-13-46.us-west-1.compute.amazonaws.com "sudo chmod 777 /var/run/docker.sock"
```
create a job to build app: https://homework-jenkins.ddns.net:30036/job/build_app/

## prepare resources for app
```hcl
cd deploy/app
ek create ns homework
terraform apply
'''

ekh get secret app-token-s5c5l -o jsonpath='{.data.ca\.crt}'
ekh get secret app-token-s5c5l -o jsonpath='{.data.token}' | base64 --decode
