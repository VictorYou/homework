#!/bin/bash

download_chart()
{
  echo "[INFO]: download charts"
  rm -rf mysql*.tgz nginx*.tgz
  rm -rf charts/*

  sudo helm repo add stable https://kubernetes-charts.storage.googleapis.com
  sudo helm fetch stable/mysql
  sudo helm fetch bitnami/nginx
  
  tar zxvf mysql*.tgz -C charts
  tar zxvf nginx*.tgz -C charts
}

update_nginx_chart_values ()
{
  local values_file='charts/nginx/values.yaml'

  cat >> charts/nginx/values.yaml <<EOF
serverBlock: |-
  server {
    listen 8443 ssl;
    ssl_certificate           /etc/secrets/certificate;
    ssl_certificate_key       /etc/secrets/private_key;
    ssl_session_cache  builtin:1000  shared:SSL:10m;
    ssl_protocols  TLSv1.2;
    ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
    ssl_prefer_server_ciphers on;

    server_name _;
    location / {
      proxy_set_header X-Forwarded-Proto https;
      proxy_redirect off;
      proxy_pass http://tvnf-rest:8000;
    }
  }
EOF
  sed -ri 's|(type: )(.*)|\1NodePort|' "$values_file"
  sed -ri 's|(httpsPort: )(.*)|\18443|' "$values_file"
  sed -ri 's|(https: )(.*)|\132443|' "$values_file"
}

update_nginx_chart_deployment ()
{
  local deployment_file='charts/nginx/templates/deployment.yaml'

  sed -ri 's|(volumes:)|\1\n        - name: secrets\n          hostPath:\n            path: /etc/secrets\n            type: Directory|' "$deployment_file"
  sed -ri 's|(volumeMounts:)|\1\n            - name: secrets\n              mountPath: /etc/secrets|' "$deployment_file"
}

update_nginx_chart_svc ()
{
  local svc_file='charts/nginx/templates/svc.yaml'

  sed -ri 's|(targetPort: )(https)|\1{{ .Values.service.httpsPort }}|' "$svc_file"
}

update_nginx_chart ()
{
  echo "[INFO]: update nginx chart"

  update_nginx_chart_values
  update_nginx_chart_deployment
  update_nginx_chart_svc
}

update_mysql_chart()
{
  echo "[INFO]: update mysql chart"
  echo >> charts/mysql/values.yaml
  cat >> charts/mysql/values.yaml <<EOF
mysqlRootPassword: Yh123$%^
mysqlUser: testvnf
mysqlPassword: Yh123$%^
mysqlDatabase: testvnf
EOF
}

main()
{
  download_chart
  update_nginx_chart
  update_mysql_chart
}

main
