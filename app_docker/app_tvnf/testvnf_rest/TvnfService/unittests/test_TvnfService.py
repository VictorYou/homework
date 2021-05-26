import unittest
import json
import xml.etree.ElementTree as ET
import os
import sys
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
print(f"{parent_dir}")
print(f"{os.path.dirname(parent_dir)}")
sys.path.append(parent_dir)
sys.path.append(os.path.dirname(parent_dir))
from robot.api import get_model
from TestVnfActions import SaveLabData, SaveNEData, TestVnfActions
from TestcaseActions import TestcaseActions, TestcaseList, TestcaseListFiltered
from TestcaseActions import TestVisitor

class TestSetupEnvReq(unittest.TestCase):
  maxDiff = None
  def test_save_lab_info_add(self):
    data_json = json.loads('{"lab_name": "clab1815", "omc_password": "1815--User", "root_password": "arthur", "vm3dn": "clab1815node01.netact.nsn-rdnet.net", "netact_host": "10.32.214.236", "netact_lbwas": "clab3417lbwas.netact.nsn-rdnet.net", "dn": "PLMN-PLMN/MRBTS-801", "mr": "MRC-MRC/MR-BTSMED"}')
    setup_request = SaveLabData(data_json)
    lab_data = '{"NeVeLabs": {}}'
    expected_result = json.loads('{"NeVeLabs": {"clab1815": {"omc_password": "1815--User", "root_password": "arthur", "vm3dn": "clab1815node01.netact.nsn-rdnet.net", "netact_host": "10.32.214.236", "netact_lbwas": "clab3417lbwas.netact.nsn-rdnet.net", "dn": "PLMN-PLMN/MRBTS-801", "mr": "MRC-MRC/MR-BTSMED"}}}')
    self.assertEqual(setup_request.get_new_data(lab_data), expected_result)

  def test_save_lab_info_modify(self):
    data_json = json.loads('{"lab_name": "clab1815", "omc_password": "1815--User", "root_password": "arthur", "vm3dn": "clab1815node01.netact.nsn-rdnet.net"}')
    setup_request = SaveLabData(data_json)
    lab_data = '{"NeVeLabs": {"clab1815": {"omc_password": "omc", "root_password": "root", "vm3dn": "clab1815node02.netact.nsn-rdnet.net"}}}'
    expected_result = json.loads('{"NeVeLabs": {"clab1815": {"omc_password": "1815--User", "root_password": "arthur", "vm3dn": "clab1815node01.netact.nsn-rdnet.net"}}}')
    self.assertEqual(setup_request.get_new_data(lab_data), expected_result)

  def test_save_ne_info_add(self):  
    data_json = json.loads('{"ne_name": "SMM_111", "ne_class": "SMM", "ne_ip": "2a00:8a00:4000:20c:0:0:1c:16", "ne_instance": "111", "ne_sw": "1805", "mrbts_address": "mrbts-801.netact.com", "neac_service_types": ["SOAM Web Service Access", "NWI3 Access"]}')
    setup_request = SaveNEData(data_json)
    ne_data = '<?xml version="1.0" encoding="UTF-8"?><NetworkElements></NetworkElements>'
    expected_result_str = '''<NetworkElements><SMM_111><ne_class value="SMM" /><ne_ip value="2a00:8a00:4000:20c:0:0:1c:16" /><ne_instance value="111" /><ne_sw value="1805" /><mrbts_address value="mrbts-801.netact.com" /><neac_service_types type="list" value="'SOAM Web Service Access', 'NWI3 Access'" /></SMM_111></NetworkElements>'''
    result = setup_request.get_new_data(ne_data)
    self.assertEqual(ET.tostring(result, encoding='unicode', method='xml'), expected_result_str)

  def test_save_ne_info_modify(self):  
    data_json = json.loads('{"ne_name": "SMM_111", "ne_class": "SMM", "ne_ip": "2a00:8a00:4000:20c:0:0:1c:16", "ne_instance": "111", "ne_sw": "1805"}')
    setup_request = SaveNEData(data_json)
    ne_data = '<?xml version="1.0" encoding="UTF-8"?><NetworkElements><SMM_111><ne_class value="SMM" /><ne_ip value="2a00:8a00:4000:20c:0:0:1c:16" /><ne_instance value="1" /><ne_sw value="18" /></SMM_111></NetworkElements>'
    expected_result_str = '<NetworkElements><SMM_111><ne_class value="SMM" /><ne_ip value="2a00:8a00:4000:20c:0:0:1c:16" /><ne_instance value="111" /><ne_sw value="1805" /></SMM_111></NetworkElements>'
    result = setup_request.get_new_data(ne_data)
    self.assertEqual(ET.tostring(result, encoding='unicode', method='xml'), expected_result_str)


  def test_get_testcases_filtered(self):
    expected_list = [
      {'title': 'Create SFTP user in NEAC', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'NEAC', 'USER_CREATION']), 'description': 'This test case creates the SFTP Access credential in Network Element Access Control to enable the communication for the support of Dynamic Adaptation.', 'folder': 'unittests', 'filename': 'tc_reg_CORE_NTHLRFE_NEIW_integration.robot', 'suite': 'tc reg CORE NTHLRFE NEIW integration'},
      {'title': 'Create NEAC Service Users', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'NEAC', 'USER_CREATION']), 'description': 'This test case checks whether the needed credentials for NE integration are created. If not, it creates the credentials.', 'folder': 'unittests', 'filename': 'tc_reg_CORE_NTHLRFE_NEIW_integration.robot', 'suite': 'tc reg CORE NTHLRFE NEIW integration'},
    ]
    result_list = TestcaseListFiltered().get(current_dir, 'NEAC')
    self.assertEqual(result_list, expected_list)


class TestTestVisitor(unittest.TestCase):
  def test_get_testcases_in_a_file(self):
    expected_list = [
      {'title': 'Create SFTP user in NEAC', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'NEAC', 'USER_CREATION']), 'description': 'This test case creates the SFTP Access credential in Network Element Access Control to enable the communication for the support of Dynamic Adaptation.'},
      {'title': 'Create NEAC Service Users', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'NEAC', 'USER_CREATION']), 'description': 'This test case checks whether the needed credentials for NE integration are created. If not, it creates the credentials.'},
      {'title': 'NTHLRFE NEIW', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'NEIW']), 'description': 'In this test case, NEIW for LTE OMS is executed.'},
      {'title': 'Configuring SSH connection between NTHLRFE and NetAct', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'SSH_CONNECTION']), 'description': 'This test case configures SSH connection between NT HLR FE and NetAct.'},
      {'title': 'Verify Alarm Upload', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'ALARM_UPLOAD', 'MONITOR', 'VERIFY']), 'description': 'This test case uploads alarm for NTHLRFE managed object and verifies if it is successful.'},
      {'title': 'Verify CM Upload', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'CMOP', 'CM_UPLOAD', 'VERIFY']), 'description': 'This test case verifies configuration management in CM Operations Manager for successful NE integration.'}]
    model = get_model(f'{current_dir}/tc_reg_CORE_NTHLRFE_NEIW_integration.robot')
    visitor = TestVisitor()
    visitor.visit(model)
    self.assertEqual(visitor.testcases, expected_list)


class TestTestTestcaseList(unittest.TestCase):
  maxDiff = None
  def test_get_testcases(self):
    expected_list = [
      {'suite': 'tc reg CORE NTHLRFE NEIW integration', 'title': 'Create SFTP user in NEAC', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'NEAC', 'USER_CREATION']), 'description': 'This test case creates the SFTP Access credential in Network Element Access Control to enable the communication for the support of Dynamic Adaptation.', 'folder': 'unittests', 'filename': 'tc_reg_CORE_NTHLRFE_NEIW_integration.robot'},
      {'suite': 'tc reg CORE NTHLRFE NEIW integration', 'title': 'Create NEAC Service Users', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'NEAC', 'USER_CREATION']), 'description': 'This test case checks whether the needed credentials for NE integration are created. If not, it creates the credentials.', 'folder': 'unittests', 'filename': 'tc_reg_CORE_NTHLRFE_NEIW_integration.robot'},
      {'suite': 'tc reg CORE NTHLRFE NEIW integration', 'title': 'NTHLRFE NEIW', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'NEIW']), 'description': 'In this test case, NEIW for LTE OMS is executed.', 'folder': 'unittests', 'filename': 'tc_reg_CORE_NTHLRFE_NEIW_integration.robot'},
      {'suite': 'tc reg CORE NTHLRFE NEIW integration', 'title': 'Configuring SSH connection between NTHLRFE and NetAct', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'SSH_CONNECTION']), 'description': 'This test case configures SSH connection between NT HLR FE and NetAct.', 'folder': 'unittests', 'filename': 'tc_reg_CORE_NTHLRFE_NEIW_integration.robot'},
      {'suite': 'tc reg CORE NTHLRFE NEIW integration', 'title': 'Verify Alarm Upload', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'ALARM_UPLOAD', 'MONITOR', 'VERIFY']), 'description': 'This test case uploads alarm for NTHLRFE managed object and verifies if it is successful.', 'folder': 'unittests', 'filename': 'tc_reg_CORE_NTHLRFE_NEIW_integration.robot'},
      {'suite': 'tc reg CORE NTHLRFE NEIW integration', 'title': 'Verify CM Upload', 'tags': sorted(['CRITICAL', 'INTEGRATE_NE', 'NTHLRFE_NEIW', 'DEVOPS', 'CMOP', 'CM_UPLOAD', 'VERIFY']), 'description': 'This test case verifies configuration management in CM Operations Manager for successful NE integration.', 'folder': 'unittests', 'filename': 'tc_reg_CORE_NTHLRFE_NEIW_integration.robot'}]
    result_list = TestcaseList().get(current_dir)
    self.assertEqual(result_list, expected_list)


class TestTestcaseActions(unittest.TestCase):
  maxDiff = None
  def test_parse_result_file(self):
    expected_list = [{'name': 'Create MR', 'result': 'pass'},
    {'name': 'Create SFTP user in NEAC', 'result': 'pass'},
    {'name': 'Create NEAC Service Users', 'result': 'pass'},
    {'name': 'NTHLRFE NEIW', 'result': 'fail'},
    {'name': 'Configuring SSH connection between NTHLRFE and NetAct', 'result': 'fail'},
    {'name': 'Verify Alarm Upload', 'result': 'fail'},
    {'name': 'Verify CM Upload', 'result': 'fail'}
    ]
    self.assertEqual(TestcaseActions().parse_result_file(f'{current_dir}/result.xml'), sorted(expected_list, key=lambda k: k['name']))
    
  def test_get_test_result_summary(self):  
    expected_summary = "3 passes, 4 fails"
    result_list = [{'name': 'Create MR', 'result': 'pass'},
    {'name': 'Create SFTP user in NEAC', 'result': 'pass'},
    {'name': 'Create NEAC Service Users', 'result': 'pass'},
    {'name': 'NTHLRFE NEIW', 'result': 'fail'},
    {'name': 'Configuring SSH connection between NTHLRFE and NetAct', 'result': 'fail'},
    {'name': 'Verify Alarm Upload', 'result': 'fail'},
    {'name': 'Verify CM Upload', 'result': 'fail'}
    ]
    self.assertEqual(TestcaseActions().test_result_summary(result_list), expected_summary)


if __name__ == '__main__':
    unittest.main()
