import os
import json
import requests
from requests_toolbelt import MultipartEncoder
from log import log

# NDAP_URL = 'https://10.55.76.52'
NDAP_URL = os.environ['NDAP_URL'] + '/'
NDAP_TVNFI_BASE_URL = NDAP_URL + 'ndap/v1'
TVNF_NAME = os.environ['TVNF_NAME']
TVNF_VERSION = os.environ['TVNF_VERSION']
LONG_LIVED_JWT = os.environ['LONG_LIVED_JWT']
NDAP_CA_FILE = os.environ['NDAP_CA_FILE']


class NdapCommunicator(object):
  """
  Handles communication from Test VNF to NDAP
  """
  headers = {'Authorization': f'JWT {LONG_LIVED_JWT}'}

  def register_req(self, tvnfId):
    log.debug('in NdapCommunicator().register_req')
    vnf_type = TVNF_NAME
    data = {'tvnfId': tvnfId, 'version': TVNF_VERSION, 'vnfType': vnf_type}
    log.debug(f'data: {data}')
    response = self._send('POST', 'ndap/v1/testvnfs', json=data)
    log.debug(f'response: {response.text}')

  def failed_req(self, tvnfId, sutId):
    log.debug('in NdapCommunicator().failed_req')
    end_point = f'ndap/v1/testvnfs/{tvnfId}/suts/{sutId}'
    response = self._send('POST', end_point, json={})
    log.debug(f'response: {response.text}')

  def setup_env_result_req(self, result, testcases, sutId, tvnfId):
    log.debug('in NdapCommunicator().setup_env_result_req')
    data = {'result': result}
    data['testcases'] = testcases
    data['sutId'] = sutId
    data['tvnfId'] = tvnfId
    end_point = f'ndap/v1/testvnfs/{tvnfId}/suts/{sutId}/envSetupResult'
    log.debug(f'data: {data}')
    response = self._send('POST', end_point, json=data)
    log.debug(f'response: {response.text}')

  def report_test_result_req(self, sessionId, log_filename, tc_result):
    log.debug('in NdapCommunicator().report_test_result_req')
    ReportTestResultReq_url = NDAP_TVNFI_BASE_URL + '/testResults/' + sessionId
    log.debug(f'ReportTestResultReq_url: {ReportTestResultReq_url}')
    headers = self.headers.copy()
    for result in tc_result:
      tc_result_to_send = json.dumps({'info': result})
      log.debug(f'tc_result_to_send: {tc_result_to_send}')
      encoder = MultipartEncoder({'TestResults': tc_result_to_send, 'logfile': (log_filename, open(log_filename, 'rb'))})
      headers['Content-Type'] = encoder.content_type
      response = requests.put(ReportTestResultReq_url, data=encoder, headers=headers, verify=NDAP_CA_FILE)
      log.debug(f'response: {response.text}')

  def test_execution_finished_req(self, sessionId, summary):
    log.debug('in NdapCommunicator().test_execution_finished_req')
    end_point = f'ndap/v1/testReport/{sessionId}'
    response = self._send('POST', end_point, json={'summary': summary})
    log.debug(f'response: {response.text}')

  def _send(self, method, end_point, *args, **kwargs):
    log.debug('in NdapCommunicator()._send')
    try:
      kwargs['verify'] = NDAP_CA_FILE
      kwargs['headers'] = self.headers
      request_url = NDAP_URL + end_point
      log.debug(f'request url: {request_url}')
      response = requests.request(method, request_url, *args, **kwargs)
      log.debug(f'response: {response.text}')
      return response
    except Exception as e:
      log.debug(f'exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}')
