FROM ubuntu:latest
MAINTAINER 361551968@qq.com

RUN apt-get update
RUN apt install -y tzdata
RUN echo "Asia/Beijing" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
RUN apt-get update
RUN apt install -y \
  curl \
  python3.8-dev \
  python3-pip \
  libmysqlclient-dev \
  mysql-client \
  libssl-dev \
  expect \
  iputils-ping \
  inetutils-traceroute \
  zip

RUN pip3 install requests-toolbelt \
  && pip3 install paramiko \
  && pip3 install Django \
  && pip3 install robotframework \
  && pip3 install djangorestframework \
  && pip3 install mysqlclient

RUN apt install -y vim

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

COPY app_tvnf/ /home/testvnf/

RUN ls -la /home/testvnf/

ENTRYPOINT ["/bin/sh", "-c"] 
CMD ["env"]

