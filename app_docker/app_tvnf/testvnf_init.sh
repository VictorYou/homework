#!/bin/bash -xe


function main()
{
  local current_dir=$(dirname $0)
  local manage_py="$current_dir/testvnf_rest/manage.py"
  local svc_mysql=$1
  
  echo "[INFO]: migrate db"
  python3 "$manage_py" makemigrations AppService
  python3 "$manage_py" migrate
  
  echo "[INFO]: alter character set"
  mysql -h $svc_mysql -P3306 -u testvnf -pYh123$%^ < "$current_dir/alter_db_character_set.sql"
  
  echo "[INFO]: create django user with ndap password"
#  echo "from django.contrib.auth.models import User; User.objects.create_superuser('ndap', 'admin@example.com', 'pass')" > /home/create_django_user
#  sed -ri "s:pass:$NDAP_PASSWORD:" /home/create_django_user
#  python3 "$manage_py" shell < /home/create_django_user
  python3 "$manage_py" shell -c """
from django.contrib.auth.models import User
import django.contrib.auth.models
try:
  user = User.objects.get(username='ndap')
  print('ndap user exists, skip creation')
except User.DoesNotExist:
  User.objects.create_superuser('ndap', 'admin@example.com', '${NDAP_PASSWORD}')
"""
  
  echo "[INFO]: start django"
  python3 "$manage_py" runserver 0:8000
}


if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  main "$@"
fi
