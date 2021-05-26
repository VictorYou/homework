import os
import inspect
import sys
import subprocess
import re
import time
import xml.etree.ElementTree as ET
#from robot.parsing.model import TestData
import ast
import robot
from robot.api import get_model

from django.db.transaction import atomic
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)
from log import log
from CaseList import CASE_LIST


DIR_TVNF_PARENT = os.environ['DIR_TVNF_PARENT']      # /tmp
LOG_DIR_TVNF_PARENT = f'{DIR_TVNF_PARENT}/logs'      # /tmp/logs
TA_DIR_TVNF_PARENT = f'{DIR_TVNF_PARENT}/NeVe_TA_RF' # /tmp/NeVe_TA_RF/
TVNF_NAME = os.environ['TVNF_NAME']                  # fastpass-tvnf-1
TA_IMAGE = os.environ['TA_IMAGE']                    # fastpass-testing-docker-local.esisoj70.emea.nsn-net.net/neveexec_master:0.0.11
NAMESPACE = os.environ['NAMESPACE']                  # fastpass-tvnf

class TestcaseActions:
  def run_testcase(self, suite, id, folder, sessionId, lab_name, ne_name, result_q):
    log.debug(f'in TestcaseActions().run_testcase, lineno: {inspect.currentframe().f_lineno}')
    from .models import Testcase
    case = Testcase.objects.get(id=id)
    name, tag = case.name, case.tags
    case_specific = re.sub('[ +_&.:]', '-', f"{sessionId.split('-')[0]}-{id}-{suite[:20]}-{name}")[:150]
    log.debug(f'case_specific: {case_specific}')
    log_dir_tvnf = f'{LOG_DIR_TVNF_PARENT}/{case_specific}/output/' # /tmp/logs/1f00-267-02--tc-open-and-Lau/output/
    log_file_dir_tvnf = f'{LOG_DIR_TVNF_PARENT}/{case_specific}/' # /tmp/logs/1f00-267-02--tc-open-and-Lau/
    test_runner = TestRunner(lab_name, ne_name, tag, sessionId, folder, log_dir_tvnf, case_specific)
    test_runner.run_test()
    result_list = self.get_result_list(case_specific, log_dir_tvnf)
    log_file = f'{log_file_dir_tvnf}/logfile_{case_specific}.zip'
    log.debug(f'log_file: {log_file}')
    self.archive_log_file(log_file, log_dir_tvnf)
    tc_result_list = self.handle_result_list(result_list)
    result_q.put(log_file, 1)
    result_q.put(tc_result_list, 1)

  def create_tauser(self, sessionId, lab_name, ne_name):
    log.debug(f'in TestcaseActions().create_tauser, lineno: {inspect.currentframe().f_lineno}')
    case_specific = f"{sessionId.split('-')[0]}-create-ta-user"
    log_dir_tvnf = f'{LOG_DIR_TVNF_PARENT}/{case_specific}/output/'
    log.debug(f'log_dir_tvnf: {log_dir_tvnf}')
    test_runner_create_tauser = TestRunnerCreateTAUser(lab_name, ne_name, sessionId, log_dir_tvnf, case_specific)
    test_runner_create_tauser.run_test()

  def stop_test(self, sessionId):
    log.debug('in TestcaseActions().stop_test')
    TestRunner.stop_test(sessionId)

  def get_cases_by_folder(self, testcases):
    from .models import Testcase
    log.debug('in TestcaseActions().get_cases_by_folder')
    folders = [x.folder for x in Testcase.objects.all()]
    folders = list(set(folders))                        # remove duplicate folder names
    log.debug(f'folders: {folders}')
    cases_by_folder = {}
    for folder in folders:
      cases_by_folder[folder] = []
    for tc in testcases:
      try:
        log.debug(f'tc: {tc}')
        case = Testcase.objects.get(id=tc)
        log.debug(f'tc: {tc}')
        log.debug(f'case.tags: {case.tags}')
        cases_by_folder[case.folder].append(case.tags)
      except Exception as e:
        log.debug(f'error in checking Testcase, {type(e)}, {e.args}, {e}, {e.__doc__}')
        pass
    for folder in folders:
      cases_by_folder[folder] = ','.join(cases_by_folder[folder])
    cases_by_test_folder = {k: v for k, v in cases_by_folder.items() if v != ''}
    log.debug(f'cases_by_test_folder: {cases_by_test_folder}')  # {'level3': 'ADAPTATION_MANAGER&CRITICAL'}
    return cases_by_test_folder

  def get_cases_by_suite(self, testcases):
    from .models import Testcase
    log.debug('in TestcaseActions().get_cases_by_suite')
    suites_folders = {}
    for x in Testcase.objects.all():
      suites_folders[x.suite] = x.folder
    suites = suites_folders.keys()
    log.debug(f'suites: {suites}')
    cases_by_suite = {}
    for suite in suites:
      cases_by_suite[suite] = {'ids': [], 'folder': suites_folders[suite]}
    for tc in testcases:
      try:
        log.debug(f'tc: {tc}')
        case = Testcase.objects.get(id=tc)
        log.debug(f'case.id: {case.id}, case.suite: {case.suite}')
        cases_by_suite[case.suite]['ids'].append(str(case.id))
      except Exception as e:
        log.debug(f'error in checking Testcase, {type(e)}, {e.args}, {e}, {e.__doc__}')
        pass
    for suite in suites:
      cases_by_suite[suite]['ids'] = ','.join(cases_by_suite[suite]['ids'])
    cases_by_suite = {k: v for k, v in cases_by_suite.items() if v['ids'] != ''}
    log.debug(f'cases_by_suite: {cases_by_suite}')  # [{'suite1': {'folder': 'level3', 'cases': 'CM Upload: Verify CM Upload'}]
    return cases_by_suite

  def get_result_list(self, case_specific, log_dir):
    log.debug('in TestcaseActions().get_result_list')
    filename = f'run-testcases_{case_specific}.xml'
    command = f'rebot -x "{filename}" "{log_dir}"/NeVe-TA_output.xml'
    os.system(command)
    return self.parse_result_file(filename)

  def test_result_summary(cls, result_list):
    log.debug('in TestcaseActions().test_result_summary')
    success = sum(value['result'] == 'pass' for value in result_list)
    fail = sum(value['result'] == 'fail' for value in result_list)
    return f"{success} passes, {fail} fails"

  def handle_result_list(cls, result_list):
    log.debug('in TestcaseActions().handle_result_list')
    from .models import Testcase
    result_list_checked = result_list.copy()
    for result in result_list:
      log.debug(f'result to check: f{result}')
      try:
        if result['name'] not in CASE_LIST:
          log.debug(f"{result['name']} is not in test case list.")
          continue
        test = Testcase.objects.get(name=result['name'])
        result['testCaseId'] = str(test.id)
      except Exception as e:
        log.debug(f'exception caught: {type(e)}, {e.args}, {e}, {e.__doc__}, case for {result} does not exist, removing it')
        result_list_checked.remove(result)      # remove cases for creating tauser
    log.debug(f'result_list_checked: {result_list_checked}')
    return result_list_checked

  def parse_result_file(cls, file):
    log.debug('in TestcaseActions().parse_result_file')
    result_list = []
    with open(file, 'r') as file:
      tree = ET.parse(file)

    root = tree.getroot()
    for tc in root:
      result = {}
      result['name'] = tc.attrib['name']
      if len(tc) == 0:
        result['result'] = 'pass'
      else:
        result['result'] = 'fail'
      result_list.append(result)
    result_list_sorted = sorted(result_list, key=lambda k: k['name'])
    log.debug(f'result_list_sorted: {result_list_sorted}')
    return result_list_sorted

  def archive_log_file(self, log_file, log_dir):
    log.debug('in TestcaseActions().archive_log_file')
    command = f'zip -j -r "{log_file}" "{log_dir}"'
    log.debug(f'command: {command}')
    os.system(command)
    command = f'rm -rf {log_dir}'
    log.debug(f'command: {command}')
    os.system(command)

class TestVisitor(ast.NodeVisitor):
  def __init__(self):
    self.force_tags = []
    self.default_tags = []
    self.testcases = []
  def visit_ForceTags(self, node):
    self.force_tags = list(node.values)
  def visit_DefaultTags(self, node):
    self.default_tags = list(node.values)
  def visit_Tags(self, node):
    self.tags = list(node.values)
  def visit_TestCase(self, node):
    tc = {'title': node.name}
    docs = [e for e in node.body if isinstance(e, robot.parsing.model.statements.Documentation)]
    tc['description'] = docs[0].value.replace('\\n', '\n\n').replace(r'*', r'**') if len(docs) > 0 else "NO_TESTCASE_DOCUMENTATION"
    tags = [item for sublist in [e.values for e in node.body if isinstance(e, robot.parsing.model.statements.Tags)] for item in sublist]
    if len(tags) > 0:           # skip the cases with no tags
      tags += self.force_tags + self.default_tags
      tags.sort()
      tc['tags'] = tags
      self.testcases.append(tc)


class TestcaseList():
  def get(self, suitesDir):
    log.debug('in TestcaseActions().get_testcases')
    log.debug(f'suitesDir: {suitesDir}')
    testcases = []

    for dirName, subdirList, fileList in os.walk(suitesDir):
      for fname in [f for f in fileList if f.endswith(".tsv") or f.endswith(".robot")]:
        log.debug(f'fname: {fname}')
        tc_file = os.path.join(dirName, fname)
        model = get_model(tc_file)
        visitor = TestVisitor()
        visitor.visit(model)
        for tc in visitor.testcases:
          tc['folder'] = os.path.basename(suitesDir)
          tc['filename'] = fname
          tc['suite'] = fname.split('.')[0].replace('_', ' ')
        testcases += visitor.testcases
    return testcases


class TestcaseListFiltered(TestcaseList):
  def get(self, suitesDir, tag):
    testcases = super().get(suitesDir)
    testcases_filtered = [x for x in testcases if tag in x['tags']]
    return testcases_filtered


class TestRunner:
  """
  Handles tests
  """

  def __init__(self, lab_name, ne_name, tags, sessionId, folder, log_dir_tvnf, case_specific):
    log.debug('in TestRunner().__init__')
    self.lab_name = lab_name
    self.ne_name = ne_name
    self.tags = tags
    self.sessionId = sessionId
    self.folder = folder
    self.log_dir_tvnf = log_dir_tvnf             # /home/testvnf/logs/1f00-267-02--tc-open-and-Lau/output/
    log.debug(f'log_dir_tvnf: {self.log_dir_tvnf}')
    self.log_dir_container = f'/tmp/logs/'
    self.case_specific = case_specific
    self.test_name = f'tester-{case_specific}'.lower()[:63].rstrip('-')
    log.debug(f'test runner created, with folder: {folder}')

  def prepare_test(self):
    log.debug('in TestRunner().prepare_test')
    if not os.path.exists(self.log_dir_tvnf):
      command = f'mkdir -p "{self.log_dir_tvnf}"'
      log.debug(f'command: {command}')
      os.system(command)
    command = f'chmod 777 "{self.log_dir_tvnf}"'
    log.debug(f'command: {command}')
    os.system(command)

  def session_available(self):
    from .models import TestExecution, TestSession
    log.info(f'in TestRunner().session_available')
    if len(TestSession.objects.filter(sessionId=self.sessionId)) == 0 or TestSession.objects.get(sessionId=self.sessionId).status != 'A':
      return False
    return True

  def run_test(self):
    from .models import TestExecution
    log.debug('in TestRunner().run_test')
    self.prepare_test()
    while True:
      if not self.session_available():
        log.info(f'session {self.sessionId} not available, do not start new tests, exiting...')
        sys.exit(1)
      ret = os.system(self.test_command())
      if ret == 0:
        break
      log.debug('test not started, retry in 60s')
      time.sleep(60)

    log.debug('starting the test ...')
    with atomic():
      execution, created = TestExecution.objects.get_or_create(testname=self.test_name, status='A')
      execution.sessionId = self.sessionId
      execution.save()
    log_identifier = self.test_name
    log.debug(f'{log_identifier}: test started')
    counter = 0
    while True:
      os.system('sleep 10')
      execution = TestExecution.objects.get(testname=self.test_name)
      if execution is not None and execution.status != 'A':
        log.debug('test is aborted ... exiting')
        subprocess.Popen(f'kubectl delete pod {self.test_name} --force --grace-period 0', shell=True, stdout=subprocess.PIPE).wait()
        with atomic():
          from .models import TestExecution, TestSession
          log.info(f'to delete test execution: {execution.testname}')
          execution.delete()
          log.info('test execution deleted')
          if len(TestExecution.objects.filter(sessionId=self.sessionId)) == 0:
            log.info(f'to delete session: {self.sessionId}')
            TestSession.objects.get(sessionId=self.sessionId).delete()
            log.info(f'session deleted: {self.sessionId}')
        sys.exit(1)
      command = f'kubectl get po {self.test_name} -o go-template' +  " --template '{{ .status.phase }}'" 
      status = re.sub('"', '', os.popen(command).read().strip())
      log.debug(f'{log_identifier}: status: {status} for {10*counter}s')
      if status != 'Running' and status != 'Pending':
        log.debug(f'{log_identifier}: tests are done, exiting')
        break
      counter += 1
    subprocess.Popen(f'kubectl delete pod {self.test_name} --force --grace-period 0', shell=True, stdout=subprocess.PIPE).wait()
    with atomic():
      execution = TestExecution.objects.get(testname=self.test_name)
      if execution is not None:
        execution.delete()

  def test_command(self):
    log.debug('in TestRunner().test_command')
    ta_root_dir = '/home/tauser/NeVe_TA_RF'
    tvnf_name = TVNF_NAME
    command = f'''kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: {self.test_name}
  namespace: {NAMESPACE}
spec:
  serviceAccountName: tvnf
  restartPolicy: Never
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  containers:
  - name: {self.test_name}
    image: {TA_IMAGE}
    imagePullPolicy: IfNotPresent
    resources:
      requests:
        memory: "1Gi"
        cpu: "200m"
    env:
    - name: LAB
      value: {self.lab_name}
    - name: NE_NAME
      value: {self.ne_name}
    - name: TAGS
      value: {self.tags}
    - name: TEX_BROWSER
      value: Chrome
    - name: SESSION_ID
      value: '{self.case_specific}'
    - name: FOLDER
      value: {self.folder}
    command: [ "/bin/bash", "-cx", "--" ]
    args: [ "bash {ta_root_dir}/no_jenkins.sh" ]
    volumeMounts:
    - name: {tvnf_name}-ta
      mountPath:  {ta_root_dir}
    - name: {tvnf_name}-log
      mountPath:  {self.log_dir_container}
  imagePullSecrets:
  - name: registrykey-{tvnf_name}
  volumes:
    - name: {tvnf_name}-ta
      persistentVolumeClaim:
        claimName: {tvnf_name}-ta
    - name: {tvnf_name}-log
      persistentVolumeClaim:
        claimName: {tvnf_name}-log
  nodeSelector:
    role: testvnf
EOF'''
    log.debug(f'command: {command}')
    return command

  @classmethod
  def stop_test(self, sessionId):
    log.debug(f'in TestRunner.stop_test: {sessionId}')
    from .models import TestExecution, TestSession
    executions = TestExecution.objects.filter(sessionId=sessionId)
    for execution in executions:
      execution.status = 'U'
      execution.save()
    session = TestSession.objects.get(sessionId=sessionId)
    if session is not None:
      session.status = 'U'
      session.save()


class TestRunnerCreateTAUser(TestRunner):
  """
  Handles quality level tests, tauser need be created first, so those tags are mandatory
  """

  def __init__(self, lab_name, ne_name, sessionId, log_dir_tvnf, case_specific):
    log.debug('in TestRunnerCreateTAUser().__init__')
    super().__init__(lab_name, ne_name, 'CRITICAL&LEVEL3&CREATETAUSER&CI', sessionId, 'level3', log_dir_tvnf, case_specific)
