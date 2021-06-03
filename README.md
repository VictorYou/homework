# homework
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
eh repo add jenkins https://charts.jenkins.io
eh repo update
eh install myjenkins jenkins/jenkins --set controller.image="viyou/jenkins" --set controller.tag=latest --set controller.installPlugins=false
ek exec -it svc/myjenkins -c jenkins -- /bin/cat /run/secrets/chart-admin-password && echo
```
password is 66q6LlUXJbCf1EV8IlyjFz in this case.
apply for dynamic jenkins from https://my.noip.com, with hostname as homework-jenkins.ddns.net and ip as what you get from checking ing, 54.177.223.84, in this case
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
open browser and access https://homework-jenkins.ddns.net:32723/ jenkins with admin / 66q6LlUXJbCf1EV8IlyjFz
create a credential to access github, github-viyou in this case.
install plugins below:
   	Pipeline: Groovy 


