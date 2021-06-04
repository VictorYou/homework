FROM jenkins/jenkins

#ENV http_proxy=http://10.144.1.10:8080
#ENV https_proxy=https://10.144.1.10:8080
#ENV DOCKERVERSION=19.03.9
#RUN curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKERVERSION}.tgz \
#  && tar xzvf docker-${DOCKERVERSION}.tgz --strip 1 -C /usr/bin docker/docker \
#  && rm docker-${DOCKERVERSION}.tgz

# keys
RUN jenkins-plugin-cli --plugins pipeline-stage-step matrix-auth apache-httpcomponents-client-4-api modernstatus xvnc pipeline-model-extensions pipeline-stage-tags-metadata oauth-credentials nodelabelparameter parameterized-trigger ace-editor mapdb-api workflow-aggregator pipeline-github-lib audit-trail role-strategy pipeline-graph-analysis handlebars script-security authentication-tokens credentials simple-theme-plugin branch-api discard-old-build cloudbees-folder kubernetes vncviewer build-name-setter junit kubernetes-credentials conditional-buildstep workflow-durable-task-step envinject-api workflow-scm-step timestamper exclusive-execution credentials-binding antisamy-markup-formatter startup-trigger-plugin windows-slaves javadoc workflow-cps-global-lib pipeline-model-api icon-shim config-file-provider workflow-job code-coverage-api external-monitor-job extended-choice-parameter ssh-slaves google-oauth-plugin docker-plugin momentjs artifactory environment-script Parameterized-Remote-Trigger multi-branch-project-plugin envinject scm-api run-condition mailer job-dsl workflow-api pam-auth pipeline-utility-steps lockable-resources durable-task token-macro jquery-detached pipeline-milestone-step jquery workflow-basic-steps ivy ws-cleanup workflow-cps git-server vncrecorder workflow-step-api pipeline-build-step ldap docker-java-api gradle job-import-plugin matrix-project greenballs docker-commons docker-workflow structs github-api pipeline-input-step build-timeout kubernetes-client-api rebuild gerrit-trigger pipeline-model-definition ssh-credentials resource-disposer groovy command-launcher pipeline-stage-view trilead-api maven-plugin jdk-tool git-client next-build-number jackson2-api workflow-support bouncycastle-api email-ext cobertura urltrigger copyartifact github ant snakeyaml-api ssh-agent display-url-api github-branch-source plain-credentials pipeline-rest-api variant robot workflow-multibranch git pipeline-model-declarative-agent jsch

USER root
RUN apt-get update && \
    apt-get -qy full-upgrade && \
    apt-get install -qy curl && \
    apt-get install -qy curl && \
    curl -sSL https://get.docker.com/ | sh

RUN apt-get install -y expect

# install helm
RUN cd /home \
	&& curl https://get.helm.sh/helm-v3.6.0-linux-amd64.tar.gz -so helm.tar.gz\
	&& tar -xvf helm.tar.gz \
	&& rm helm.tar.gz \
	&& mv linux-amd64/helm /usr/local/bin/helm \
	&& chmod +x /usr/local/bin/helm \
	&& helm --help \
	&& cd

# install kubectl
RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN echo deb https://apt.kubernetes.io/ kubernetes-xenial main>/etc/apt/sources.list.d/kubernetes.list
RUN apt-get update
RUN apt-get install -y kubectl

# install aws-iam-authenticator
RUN curl -o aws-iam-authenticator https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/aws-iam-authenticator
RUN chmod +x ./aws-iam-authenticator
RUN mv ./aws-iam-authenticator /usr/local/bin/aws-iam-authenticator

USER jenkins
