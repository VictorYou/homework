# -*- coding: utf-8 -*-

from .models import Tvnf, Sut, TestSession
from .serializers import TvnfSerializer, SutSerializer

from queue import Queue
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from MySQLdb._exceptions import OperationalError

from .TestVnfActions import TestVnfActions

import threading
import time
import os
import queue

from log import log


class AbortTestExecutionReq(GenericAPIView):
  def post(self, request, sessionId, *args, **kwargs):
    ''' can test in this way:
    curl -undap:Admin123 --noproxy '*' -X POST http://127.0.0.1:8000/testvnf/v1/abortTests/123456
    curl --noproxy '*' -X POST http://tvnf-rest:8000/testvnf/v1/abortTests/123456
    curl --noproxy '*' --cacert /etc/secrets/cert -X POST https://127.0.0.1:32443/testvnf/v1/abortTests/123456
    curl --noproxy '*' --cacert cert -X POST https://10.55.76.99:443/testvnf/v1/abortTests/123456
    curl -undap:Admin123 --cacert ssl/cert --noproxy '*' -X POST https://127.0.0.1:443/testvnf/v1/abortTests/123456
    '''
    response = Response()
    try:
      log.debug(f"sessionId in AbortTestExecutionReq: {sessionId}")
      t = threading.Thread(target=self.abort, args=(sessionId,))
      t.start()
      response.data = {'result': 'OK'}
    except Exception as e:
      log.debug(f'exception caught in AbortTestExecutionReq: {type(e)}, {e.args}, {e}, {e.__doc__}')
      response.data = {'result': 'NOK'}
    return response

  def abort(self, sessionId):
    log.debug('in AbortTestExecutionReq().abort')


class SetupEnvReq(GenericAPIView):
  CURRENTDIR = os.path.dirname(os.path.realpath(__file__))
  SUITES_DIR_ROOT = f'{CURRENTDIR}/../../TA/NeVe_TA_RF/robot/tests'
  SUITES_DIR_DEVOPS = f'{SUITES_DIR_ROOT}/devops'
  SUITES_DIR_NES_AFFECTING = f'{SUITES_DIR_ROOT}/NEs_affecting'
  SUITES_DIR_LEVEL3 = f'{SUITES_DIR_ROOT}/level3'
  SUITES_DIR_LEVLE6 = f'{SUITES_DIR_ROOT}/level6'

  def post(self, request, *args, **kwargs):
    log.debug('in SetupEnvReq().post')
    response = Response()
    try:
      log.debug(f'data: {request.data}')
      t = threading.Thread(target=self.setup_env, args=(request,))
      t.start()
      response.data = {'result': 'OK'}
    except Exception as e:
      log.debug(f'exception caught in SetupEnvReq: {type(e)}, {e.args}, {e}, {e.__doc__}')
      response.data = {'result': 'NOK'}
    return response

  def setup_env(self, request):
    log.debug("haha in SetupEnvReq().setup_env")
    try:
      log.debug(f'data: {request.data}')
      sutId, tvnfId, info = request.data['sutId'], request.data['tvnfId'], request.data['deploymentInfo']
      log.debug(f'sutId: {sutId}, tvnfId: {tvnfId}, info: {info}')
      info['ne_name'] = f"{info['ne_class']}_{str(time.time())}"
      info['lab_name'] = f'clab_{str(time.time())}'
      testcases_devops = TestcaseList().get(self.SUITES_DIR_DEVOPS)
      log.debug(f"testcases_devops: {[x['title'] for x in testcases_devops]}")
      testcases_nes_affecting = TestcaseListFiltered().get(self.SUITES_DIR_NES_AFFECTING, 'INTEGRATE_NE')
      testcases_level3 = TestcaseList().get(self.SUITES_DIR_LEVEL3)
      testcases_mrbts = TestcaseListFiltered().get(self.SUITES_DIR_LEVLE6, 'MRBTS')
      log.debug(f"testcases_mrbts: {[x['title'] for x in testcases_mrbts]}")
      testcases_common_sat = TestcaseListFiltered().get(self.SUITES_DIR_LEVLE6, 'SAT')
      TestVnfActions.save_testcases(testcases_devops + testcases_nes_affecting + testcases_level3 + testcases_mrbts + testcases_common_sat)
      testcases = TestVnfActions.get_testcases_from_db()
      log.debug(f'testcases number: {len(testcases)}')
      tvnf_action = TestVnfActions(info)
      tvnf_action.create_sut(info, sutId, testcases)
      tvnf_action.create_tvnf(tvnfId)
      testcase_names = [tc['title'] for tc in testcases]
      log.debug(f'testcase_names: {testcase_names}')
      tvnf_action.save_deployment_info()
      tvnf_action.try_connect_to_lab()
      tvnf_action.save_neve_ta_rf()
      result = 'success'
    except Exception as e:
      log.debug(f'error in setting up environment: {type(e)}, {e.args}, {e}, {e.__doc__}')
      testcases = []
      result = 'failure'


class RunTestcaseReq(GenericAPIView):
  MAX_CONTAINER_COUNT = 15
  MAX_RESULT_COUNT = 200

  def post(self, request, sutId, *args, **kwargs):
    response = Response()
    try:
      testcases = request.data['testcases']
      sessionId = request.data['sessionId']
      t = threading.Thread(target=self.run_testcases, args=(testcases, sutId, sessionId,))
      t.start()
      response.data = {'result': 'OK'}
    except Exception as e:
      log.debug(f'error in starting running testcase: {type(e)}, {e.args}, {e}, {e.__doc__}')
      response.data = {'result': 'NOK'}
    return response

  def run_testcases(self, testcases, sutId, sessionId):
    log.debug('in RunTestcaseReq().run_testcases')


class ResetReq(GenericAPIView):
  def delete(self, request, sutId, *args, **kwargs):
    response = Response()
    log.debug(f"in ResetReq().delete, sutId: {sutId}")
    try:
      t = threading.Thread(target=self.reset_tvnf, args=(sutId,))
      t.start()
      response.data = {'result': 'OK'}
    except Exception as e:
      log.debug(f'exception caught in ResetReq: {type(e)}, {e.args}, {e}, {e.__doc__}')
      response.data = {'result': 'NOK'}
    return response

  def reset_tvnf(self, sutId):
    try:
      tvnf = Tvnf.objects.all()[0]
      tvnfId = tvnf.tvnfId
    except Exception as e:
      log.debug(f'exception caught in reset_tvnf: {type(e)}, {e.args}, {e}, {e.__doc__}')


class ConnectTestExecutionReq(GenericAPIView):
  def post(self, request, sessionId, *args, **kwargs):
    ''' can test in this way:
    [remote] curl --cacert ndap_ca -X POST https://fastpass-tvnf1.tvnf.ndap.local:30147/testvnf/v1/connectTests/123456
    [remote] curl --cacert ndap_ca -X POST https://10.131.67.55:32443/testvnf/v1/connectTests/123456
    [remote] curl --cacert ndap_ca -X POST https://10.131.70.81:31443/testvnf/v1/connectTests/123456  # strangely, we need wait a few minutes for this to work.
    [remote] requests.post('https://10.55.76.92:443/testvnf/v1/connectTests/123456', json={}, verify='ssl/ndap_ca').json()
    [testvnf pod] curl --noproxy '*' -X POST http://127.0.0.1:8000/testvnf/v1/connectTests/123456
    [nginx pod] curl --noproxy '*' -X POST http://tvnf-rest:8000/testvnf/v1/connectTests/123456
    [nginx pod] curl --noproxy '*' --cacert /etc/secrets/cert -X POST https://127.0.0.1:8443/testvnf/v1/connectTests/123456
    '''
    response = Response()
    try:
      log.debug(f"sessionId in ConnectTestExecutionReq: {sessionId}")
      response.data = {'result': 'OK'}
    except Exception as e:
      log.debug(f'exception caught in ConnectTestExecutionReq: {type(e)}, {e.args}, {e}, {e.__doc__}')
      response.data = {'result': 'NOK'}
    return response


class TvnfViewSet(ModelViewSet):
  queryset = Tvnf.objects.all()
  serializer_class = TvnfSerializer


class SutVnfViewSet(ModelViewSet):
  queryset = Sut.objects.all()
  serializer_class = SutSerializer
