# __author__ = 'x5luo'
import logging
import os
import re
from oss_radio_tools_lib.Remote.LocalFileOperations import LocalFileOperations
import csv


class CheckIntegrationLog(object):
    def __init__(self):
        self.local_file_operations = LocalFileOperations()
        self.LOG_DIRECTORY_PATH = self.local_file_operations.get_current_directory() + os.path.sep + "logs" + os.path.sep
        self.CHECK_LIST_PATH = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "check_list.csv"

    def get_service_name_from_log_name(self, log_file_name):
        logging.info("Get service name from log name: %s", log_file_name)
        names = log_file_name.split('_')
        service_name = None
        for i in range(len(names) - 4):
            if service_name is None:
                service_name = names[i]
            else:
                service_name += "_" + names[i]
        logging.info("Get service name: %s", service_name)
        return service_name

    def get_integration_trace_logs_content(self):
        logging.info("Get integration logs content start.")
        file_names = self.local_file_operations.get_files_name_in_directory(self.LOG_DIRECTORY_PATH)
        logs_content = {}
        for file_name in file_names:
            if file_name.find("trace") != -1:
                service_name = self.get_service_name_from_log_name(file_name)
                if not logs_content.has_key(service_name):
                    logs_content[service_name] = []
                logs_content[service_name].append(
                    self.local_file_operations.get_file_content(self.LOG_DIRECTORY_PATH + file_name))
        logging.info("Get integration logs content done.")
        return logs_content

    def get_value_from_string(self, origin_string, rex_string, key_name):
        result = re.search(rex_string, origin_string)
        if result is None:
            raise AssertionError(key_name)
        return result.groups()[0].strip()

    def get_key_information_in_file(self, logs_content, SBTS_DN, SBTS_HOST):
        logging.info("Get key information start.")
        agent_id = None
        alarm_number = None
        operation_id = None
        for log in logs_content['gep']:
            for line in log:
                if line.find("ALARM_UPLOAD_FOR_THE_AGENT") != int(-1) and line.find(
                        "Alarm upload triggered by the alarm number") != int(-1) and line.find(SBTS_DN) != int(-1):
                    agent_id = self.get_value_from_string(line, 'ALARM_UPLOAD_FOR_THE_AGENT:(\d{1,})', 'agent ID')
                    alarm_number = self.get_value_from_string(line,
                                                              'Alarm upload triggered by the alarm number:(\s+\d{1,})',
                                                              'alarm number')
                    logging.info("Get agentID: %s alarm number: %s", agent_id, alarm_number)
                    break
            if agent_id is not None and alarm_number is not None:
                break
        for log in logs_content['gep']:
            for line in log:
                if line.find('ALARM_UPLOAD_FOR_THE_AGENT') != int(-1) and line.find(str(agent_id)) != int(
                        -1) and line.find('Operation Id is') != int(-1):
                    operation_id = self.get_value_from_string(line, 'Operation Id is:(\s+\d{1,}.\d{1,}.\d{1,})',
                                                              'operation ID')
                    logging.info("Get operation ID: %s", operation_id)
                    break
            if operation_id is not None:
                break
        logging.info("Get key information done.")
        return {'AgentID': agent_id, 'AlarmUploadID': alarm_number, 'OperationID': operation_id, 'SBTS_DN': SBTS_DN,
                'SBTS_HOST': SBTS_HOST}

    def get_check_str(self, check_str, values):
        logging.info("Check :" + check_str)
        for key, value in values.items():
            # logging.info(key)
            if value is not None:
                # logging.info("Replace: " + key + " " + value)
                check_str = check_str.replace("<" + key + ">", value)
        logging.info("get check string: " + check_str)
        return check_str

    def check_points(self, check_content, check_points):
        for point in check_points:
            if point == "":
                break
            if check_content.find(point) == int(-1):
                return False
        return True

    def check_rule(self, check_name, logs_content, log_type, key_words, check_points):
        logging.info("check %s start.", check_name)
        check = False
        for log in logs_content[log_type.lower()]:
            for line in log:
                if line.find(key_words) != int(-1):
                    logging.info("Pass.")
                    check = self.check_points(line, check_points)
                    if not check:
                        raise AssertionError("check " + check_name + " failed. \n" + line)
                    break
            if check:
                break
        logging.info("check %s done.", check_name)
        return check

    def check_rules_in_checklist(self, logs_content, values):
        logging.info("Check check points in checklist file start.")
        reader = csv.reader(file(self.CHECK_LIST_PATH, 'rb'))
        for line in reader:
            if line[0] == "Module":
                continue
            check_points = line[3:]
            if not self.check_rule(line[0], logs_content, line[1], self.get_check_str(line[2], values), check_points):
                logging.info(self.get_check_str(line[2], values))
                raise AssertionError("Check " + line[0] + " failed.")
        logging.info("Check check points in checklist file done.")

    def check_integration_logs(self, SBTS_DN, SBTS_HOST, log_directory_path):
        logging.info("Check integration logs start.")
        self.LOG_DIRECTORY_PATH = log_directory_path
        logs_content = self.get_integration_trace_logs_content()
        values = self.get_key_information_in_file(logs_content, SBTS_DN, SBTS_HOST)
        print values
        self.check_rules_in_checklist(logs_content, values)
        logging.info("Check integration logs done.")

# check_integration_log = CheckIntegrationLog()
# check_integration_log.check_integration_logs("PLMN-PLMN/SBTS-1771", "10.91.227.159")
