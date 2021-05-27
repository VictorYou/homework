# -*- coding: utf-8 -*-

from .models import Sut
from .serializers import SutSerializer

from queue import Queue
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from MySQLdb._exceptions import OperationalError

import threading
import time
import os
import queue

from log import log


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
      self.setup_env(request)
      response.data = {'result': 'OK'}
    except Exception as e:
      log.debug(f'exception caught in SetupEnvReq: {type(e)}, {e.args}, {e}, {e.__doc__}')
      response.data = {'result': 'NOK'}
    return response

  def setup_env(self, request):
    log.debug("haha in SetupEnvReq().setup_env")
    log.debug(f'data: {request.data}')
    sutId, info = request.data['sutId'], request.data['deploymentInfo']
    from .models import Sut
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


class SutVnfViewSet(ModelViewSet):
  queryset = Sut.objects.all()
  serializer_class = SutSerializer
