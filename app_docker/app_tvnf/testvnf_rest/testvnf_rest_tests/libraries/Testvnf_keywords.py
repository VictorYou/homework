#!/bin/env python

#from robot.libraries.BuiltIn import BuiltIn
#import resource
import os

#ROBOT = BuiltIn()


def robot_var(variable):
  return ROBOT.get_variable_value("${%s}" % variable)

class Testvnf_keywords:
  """ Robot Keywords for resource.py

  """

#  ROBOT_LIBRARY_SCOPE = "GLOBAL"

  def testvnf_startup(self):
    manage_py = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'manage.py')
    self.__manage_py = manage_py
    command = manage_py + ' ' + 'runserver' + ' &'
    print("command: {}".format(command))
    os.system(command)
    os.system('sleep 2')

  def testvnf_teardown(self):
    pid = os.popen("ps -ef | grep manage.py | grep -v grep | awk '{print $2}' | sort -n | tail -1").read().strip()
    command = 'kill -9 ' + pid
    print("command: {}".format(command))
    os.system(command)
    command = self.__manage_py + ' ' + 'delete_sut'
    print("command: {}".format(command))
    os.system(command) 
