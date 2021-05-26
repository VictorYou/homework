import os
import json
import paramiko
import socket
import sys
import xml.etree.ElementTree as ET
from django.db.transaction import atomic
import xml.dom.minidom
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)
from log import log
from CaseList import CASE_LIST


class TestVnfActions:
  def __init__(self, deployment_info):
    self._info = deployment_info

  def save_deployment_info(self):
    log.debug('in TestVnfActions().save_deployment_info')
#    current_dir = os.path.dirname(os.path.realpath(__file__))
    lab_data_file = f'{current_dir}/../../TA/NeVe_TA_RF/configuration/nevescripts/LabData.json'
    ne_data_file = f'{current_dir}/../../TA/NeVe_TA_RF/configuration/nevescripts/ElementDataVariables.xml'
    try:
      if 'lab_name' in self._info.keys():
        SaveLabData(self._info).save_to_file(lab_data_file)
      if 'ne_name' in self._info.keys():
        SaveNEData(self._info).save_to_file(ne_data_file)
    except Exception as e:
      log.debug(f"exception when saving deployment info: {type(e)}, {e.args}, {e}, {e.__doc__}")
      pass

  def save_neve_ta_rf(self):
    log.debug('in TestVnfActions().save_neve_ta_rf')
    command = f'cp -r {current_dir}/../../TA/NeVe_TA_RF/* /tmp/NeVe_TA_RF'
    log.debug(f"command: {command}")
    os.system(command)
    
  def try_connect_to_lab(self):
    log.debug('in TestVnfActions().try_connect_to_lab')
    self._connect_to_node(self._info['vm3dn'], 'omc', self._info['omc_password'])

  def _connect_to_node(self, address, username, password):
    log.debug('in TestVnfActions()._connect_to_node')
    host = str(address)
    uname = str(username)
    pword = str(password)
    ssh = paramiko.SSHClient()

    log.debug(f'connecting {host}')
    try:
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(host, username=uname, password=pword)
    except paramiko.AuthenticationException:
      raise Exception("SSH Error: Authentication failed!")
    except socket.error:
      raise Exception("SSH Error: Server is unreachable!")

  def create_sut(self, info, sutId, testcases):
    from .models import Sut
    log.debug("in TestVnfActions().create_sut")
    try:
      sut_name = info['lab_name'] + ',' + info['ne_name']
      log.debug(f'sut_name: {sut_name}, sutId: {sutId}')
      tc_id_list = [tc['id'] for tc in testcases]
      tc_ids = ','.join(tc_id_list)
      with atomic():
        obj, created = Sut.objects.get_or_create(sutId=sutId)
        obj.name, obj.testcases, obj.sutStatus = sut_name, tc_ids, 'A'
        obj.save()
      log.debug(f'obj name: {sut_name}, testcases: {tc_ids}')
      if created:
        log.debug('Sut does not exist, now creating ...')
      else:
        log.debug('Sut already created, now updating...')
    except Exception as e:
      log.debug(f'error creating sut: {type(e)}, {e.args}, {e}, {e.__doc__}')

  def create_tvnf(self, tvnfId):
    from .models import Tvnf
    log.debug("in TestVnfActions().create_tvnf")
    try:
      with atomic():
        obj, created = Tvnf.objects.get_or_create(tvnfId=tvnfId)
    except Exception as e:
      log.debug(f'error creating testvnf: {type(e)}, {e.args}, {e}, {e.__doc__}')

  @classmethod
  def save_testcases(self, testcases):
    from .models import Testcase
    log.debug("in TestVnfActions._save_testcases")
    for tc in testcases:
      try:
        with atomic():
          obj, created = Testcase.objects.get_or_create(name=str(tc['title'][:255]))
          obj.tags = str('&'.join(tc['tags'][:1024]))
          obj.folder = str(tc['folder'][:128])
          obj.filename = str(tc['filename'][:128])
          obj.suite = str(tc['suite'][:128])
          obj.description = str(tc['description'][:256])
          obj.save()
      except Exception as e:
        log.debug(f"error saving testcases, title: {tc['title']}, description: {tc['description']}")
        log.debug(f"exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}")

  @classmethod
  def get_testcases_from_db(self):
    from .models import Testcase
    log.debug("in TestVnfActions.get_testcases_from_db")
    log.debug(f"CASE_LIST: {CASE_LIST}")
    testcases = []
    for tc in Testcase.objects.all():
      if tc.name in CASE_LIST:
        log.debug(f'tc.name: {tc.name}')
        testcase = {}
        testcase['id'] = str(tc.id)
        testcase['title'] = tc.name
        testcase['description'] = tc.description
        testcase['filename'] = tc.filename
        testcases.append(testcase)
    log.debug(f'testcases: {testcases}')
    return testcases

  def save_testexecution(self, sutId, sessionId):
    from .models import Sut, TestExecution
    log.debug('in TestVnfActions().save_testexecution')
    sut = Sut.objects.get(sutId=sutId)
    with atomic():
      testexecution = TestExecution.objects.create(sessionId=sessionId, sut=sut)
    log.debug(f'test execution created, session id: {testexecution.sessionId}')

  @classmethod
  def get_lab_ne_name(self, sutId):
    from .models import Sut
    sut = Sut.objects.get(sutId=sutId)
    names = sut.name.split(',')
    return names[0], names[1]


class HandleDeploymentInfo:
  def __init__(self, deployment_info_json):
    self._info = deployment_info_json

  def save_to_file(self, data_file):
    with open(data_file) as file:
      data = file.read()

    datas = self.get_new_data(data)
    data_tmp_file = os.path.join(os.path.dirname(data_file), 'tmp_' + os.path.basename(data_file))
    data_backup_file = os.path.join(os.path.dirname(data_file), os.path.basename(data_file) + '.save')
    log.debug(f'data_tmp_file: {data_tmp_file}')
    self.write_file(data_tmp_file, datas)
    os.rename(data_file, data_backup_file)
    os.rename(data_tmp_file, data_file)


class SaveLabData(HandleDeploymentInfo):
  def write_file(self, filename, data):
    log.debug(f'filename: {filename}')
    log.debug(f'data type: {type(data)}')
    with open(filename, "w") as file:
      file.write(json.dumps(data, indent=2, sort_keys=True))

  def get_new_data(self, lab_data_all):
    log.debug('in SaveLabData().get_new_data')
    lab_data_all_json = json.loads(lab_data_all)
    lab_datas = lab_data_all_json['NeVeLabs']
    log.debug(f"lab name: {self._info['lab_name']}")
    data_no_lab_name = {k: v for k, v in self._info.items() if k != 'lab_name'}
    lab_datas[self._info['lab_name']] = data_no_lab_name
    return lab_data_all_json


class SaveNEData(HandleDeploymentInfo):
  def write_file(self, filename, data):
    log.debug(f'filename: {filename}')
    rough_string = ET.tostring(data, 'utf-8')
    parsed = xml.dom.minidom.parseString(rough_string)
    with open(filename, "w") as file:
      file.write(parsed.toprettyxml(indent="\t"))

  def get_new_data(self, ne_data_all):
    ne_datas = ET.fromstring(ne_data_all)
    node = ne_datas.find(self._info['ne_name'])
    data_no_ne_name = {k: v for k, v in self._info.items() if k != 'ne_name'}
    if node is not None:
      for key in data_no_ne_name.keys():
        subelement = node.find(key)
        if subelement is None:
          subelement = ET.SubElement(node, key)
        subelement.attrib = {'value': self._info[key]}
    else:
      node = ET.SubElement(ne_datas, self._info['ne_name'])
      for key in data_no_ne_name.keys():
        subelement = ET.SubElement(node, key)
        value = self._info[key]
        if type(value) is list:
          subelement.attrib = {'type': 'list', 'value': ', '.join([f"'{x}'" for x in value])}
        else:
          subelement.attrib = {'value': value}
    return ne_datas
