# __author__ = 'x5luo'
import logging
import os
import time
from oss_radio_tools_lib.NetAct.NetActServiceQuery import NetActServiceQuery
from oss_radio_tools_lib.Remote.LocalFileOperations import LocalFileOperations
from xml.etree import ElementTree


class LogOperations(object):
    COMMON_MEDIATION_SERVICE_NAME = "common_mediation"
    GEP_MEDIATION_SERVICE_NAME = "fm_pipe"
    COMMON_MEDIATION_SERVICE_SAVE_LOG_NAME = "common_mediation"
    GEP_SERVICE_SAVE_LOG_NAME = "gep"
    COMMON_MEDIATION_LOG_CONF_PATH = "/opt/oss/NSN-common_mediations/smx/conf/log4j.xml"
    COMMON_MEDIATION_LOG_CONF_FILE_NAME = "log4j.xml"
    NETACT_DEFAULT_ROOT_USERANME = "root"
    NETACT_GEP_CHANGE_LOG_SCRIPT_PATH = "/opt/oss/gep/smx/tools/SetLogLevel.sh"
    NETACT_COMMON_MEDIATION_LOG_DIRECTORY_PATH = "/var/opt/oss/log/common_mediations/"
    NETACT_GEP_MEDIATION_LOG_DIRECTORY_PATH = "/var/opt/oss/log/gep/"
    NETACT_COMMON_ACTIVE_LOG_DEFAULT_NAME = "oss_activity0_0.log"
    NETACT_COMMON_TRACE_LOG_DEFAULT_NAME = "oss_trace0_0.log"
    NETACT_COMMON_ERROR_LOG_DEFAULT_NAME = "oss_error0_0.log"
    SAVE_LOG_DIRECTORY_PATH = "/var/tmp/"

    def __init__(self, remote_operations):
        self.remote_operations = remote_operations
        self.local_file_operations = LocalFileOperations()
        self.netact_service_query = NetActServiceQuery(remote_operations)
        self.common_mediation_host = None
        self.gep_mediation_host = None
        self.common_mediation_conf_local_path = self.local_file_operations.get_current_directory() + \
                                                os.path.sep+"common_mediation_conf"+os.path.sep
        self.progress_information = []

    def get_common_mediation_host(self):
        if self.common_mediation_host is None:
            self.common_mediation_host = self.netact_service_query.get_server_ip(
                self.COMMON_MEDIATION_SERVICE_NAME)
        return self.common_mediation_host

    def get_gep_mediation_host(self):
        if self.gep_mediation_host is None:
            self.gep_mediation_host = self.netact_service_query.get_server_ip(
                self.GEP_MEDIATION_SERVICE_NAME)
        return self.gep_mediation_host

    def download_configure_file_to_local(self, host, root_password):
        logging.info("Download log configure file to local start.")
        self.remote_operations.download_file_to_local(host, self.NETACT_DEFAULT_ROOT_USERANME, root_password,
                                                      self.COMMON_MEDIATION_LOG_CONF_PATH,
                                                      self.common_mediation_conf_local_path,
                                                      self.COMMON_MEDIATION_LOG_CONF_FILE_NAME)
        logging.info("Download log configure file to local done.")

    def upload_configure_file_to_remote(self, host, root_password):
        logging.info("Upload log configure file to host " + host + " start.")
        self.remote_operations.execute_command(
            "rm -rf " + self.COMMON_MEDIATION_LOG_CONF_PATH + ".upload ")
        self.remote_operations.upload_file_to_remote(host, self.NETACT_DEFAULT_ROOT_USERANME, root_password,
                                                     self.common_mediation_conf_local_path + self.COMMON_MEDIATION_LOG_CONF_FILE_NAME,
                                                     self.COMMON_MEDIATION_LOG_CONF_PATH + ".upload")
        self.remote_operations.open_conn_and_login(host, self.NETACT_DEFAULT_ROOT_USERANME, root_password)
        self.remote_operations.execute_command(
            "mv " + self.COMMON_MEDIATION_LOG_CONF_PATH + ".upload " + self.COMMON_MEDIATION_LOG_CONF_PATH)
        self.remote_operations.execute_command("chmod 600 " + self.COMMON_MEDIATION_LOG_CONF_PATH)
        self.remote_operations.execute_command("chown esbadmin " + self.COMMON_MEDIATION_LOG_CONF_PATH)
        self.remote_operations.execute_command("chgrp sysop " + self.COMMON_MEDIATION_LOG_CONF_PATH)
        logging.info("Upload log configure file to host " + host + " done.")

    def parse_common_mediation_log_configure_file(self):
        logging.info("Parse common mediation configure xml file start.")
        ElementTree.register_namespace("log4j", "http://jakarta.apache.org/log4j/")
        tree = ElementTree.ElementTree()
        tree.parse(self.common_mediation_conf_local_path + self.COMMON_MEDIATION_LOG_CONF_FILE_NAME)
        logging.info("Parse common mediation configure xml file done.")
        return tree

    def change_param_value_in_appender_in_log4j(self, tree, appender_name, param_name, value):

        appenders = tree.findall("appender")
        for appender in appenders:
            if appender.get('name') == appender_name:
                params = appender.findall('param')
                for param in params:
                    if param.get('name') == param_name:
                        param.set('value', value)
                        break
                break

    def change_logger_level_in_logger_in_log4j(self, tree, logger_name, level_value):
        loggers = tree.findall("logger")
        for logger in loggers:
            if logger.get('name') == logger_name:
                levels = logger.findall("level")
                for level in levels:
                    level.set('value', level_value)
                break

    def open_trace_log_in_log4j(self):
        logging.info("Start trace log in log4j.xml start.")
        tree = self.parse_common_mediation_log_configure_file()
        self.change_param_value_in_appender_in_log4j(tree, "mf-trace", "threshold", "DEBUG")
        self.change_logger_level_in_logger_in_log4j(tree, "org.apache.servicemix", "DEBUG")
        tree.write(self.common_mediation_conf_local_path + self.COMMON_MEDIATION_LOG_CONF_FILE_NAME, encoding="utf-8",
                   xml_declaration=True)
        logging.info("Start trace log in log4j.xml done.")

    def close_trace_log_in_log4j(self):
        logging.info("Close trace log in log4j.xml start.")
        tree = self.parse_common_mediation_log_configure_file()
        self.change_param_value_in_appender_in_log4j(tree, "mf-trace", "threshold", "OFF")
        self.change_logger_level_in_logger_in_log4j(tree, "org.apache.servicemix", "INFO")
        tree.write(self.common_mediation_conf_local_path + self.COMMON_MEDIATION_LOG_CONF_FILE_NAME, encoding="utf-8",
                   xml_declaration=True)
        logging.info("Close trace log in log4j.xml done.")

    def change_gep_log_level(self, host, root_password, value):
        logging.info("Change the gep log level in %s start.", host)
        self.remote_operations.open_conn_and_login(host, self.NETACT_DEFAULT_ROOT_USERANME, root_password)
        self.remote_operations.execute_command(self.NETACT_GEP_CHANGE_LOG_SCRIPT_PATH + " " + value)
        logging.info("Change the gep log level in %s done.", host)

    def open_common_mediation_trace_log(self, root_password):
        common_mediation_hosts = self.get_common_mediation_host().values()
        self.download_configure_file_to_local(common_mediation_hosts[0], root_password)
        self.open_trace_log_in_log4j()
        for host in common_mediation_hosts:
            logging.info("Open the common mediation trace log in %s start.", host)
            self.upload_configure_file_to_remote(host, root_password)
            logging.info("Open the common mediation trace log in %s done.", host)
        self.local_file_operations.delete_directory(self.common_mediation_conf_local_path)

    def close_common_mediation_trace_log(self, root_password):
        common_mediation_hosts = self.get_common_mediation_host().values()
        self.download_configure_file_to_local(common_mediation_hosts[0], root_password)
        self.close_trace_log_in_log4j()
        for host in common_mediation_hosts:
            logging.info("Close the common mediation trace log in %s start.", host)
            self.upload_configure_file_to_remote(host, root_password)
            logging.info("Close the common mediation trace log in %s done.", host)
        self.local_file_operations.delete_directory(self.common_mediation_conf_local_path)

    def open_gep_mediation_trace_log(self, root_password):
        gep_mediation_hosts = self.get_gep_mediation_host().values()
        for host in gep_mediation_hosts:
            logging.info("Open the gep mediation trace log in %s start", host)
            self.change_gep_log_level(host, root_password, "com.nsn FINE")
            logging.info("Open the gep mediation trace log in %s done", host)

    def close_gep_mediation_trace_log(self, root_password):
        gep_mediation_hosts = self.get_gep_mediation_host().values()
        for host in gep_mediation_hosts:
            logging.info("Close the gep mediation trace log in %s start", host)
            self.change_gep_log_level(host, root_password, "com.nsn INFO")
            logging.info("Close the gep mediation trace log in %s done", host)

    def open_integration_related_trace_log(self, root_password):
        logging.info("Open integration related trace log start")
        self.open_common_mediation_trace_log(root_password)
        self.open_gep_mediation_trace_log(root_password)
        logging.info("Open integration related trace log done")

    def start_watch_service_log(self, root_password, hosts, service_name, log_directory_path, log_names):
        logging.info("Watch %s log start.", service_name)
        for host_name, host in hosts.items():
            host_name = host_name.split('-')[-1]
            logging.info("start watch log in %s:%s", host_name, host)
            self.remote_operations.open_conn_and_login(host, self.NETACT_DEFAULT_ROOT_USERANME, root_password)
            progress = {'host': host, 'progress': []}
            for log_name in log_names:
                save_log_path = self.SAVE_LOG_DIRECTORY_PATH + service_name + "_" + host_name + "_" + log_name + \
                                str(time.time()) + ".log"
                result = self.remote_operations.execute_command(
                    "tail -f " + log_directory_path + log_name + " > " + save_log_path + " & echo $!")
                current_progress = {'progress': result[0], 'log_path': save_log_path,
                                    'save_name': service_name + "_" + host_name + "_" + log_name}
                progress['progress'].append(current_progress)
            self.progress_information.append(progress)
        logging.info("Watch %s log done.", service_name)

    def start_watch_log(self, root_password):
        logging.info("Start watch logs start.")
        collect_logs_type = [self.NETACT_COMMON_TRACE_LOG_DEFAULT_NAME, self.NETACT_COMMON_ACTIVE_LOG_DEFAULT_NAME,
                             self.NETACT_COMMON_ERROR_LOG_DEFAULT_NAME]
        common_mediation_hosts = self.get_common_mediation_host()
        self.start_watch_service_log(root_password, common_mediation_hosts, self.COMMON_MEDIATION_SERVICE_SAVE_LOG_NAME,
                                     self.NETACT_COMMON_MEDIATION_LOG_DIRECTORY_PATH, collect_logs_type)
        gep_mediation_hosts = self.get_gep_mediation_host()
        self.start_watch_service_log(root_password, gep_mediation_hosts, self.GEP_SERVICE_SAVE_LOG_NAME,
                                     self.NETACT_GEP_MEDIATION_LOG_DIRECTORY_PATH, collect_logs_type)
        print self.progress_information
        logging.info("Start watch logs done.")

    def stop_watch_logs(self, root_password):
        logging.info("Stop watch logs start.")
        for host_progress in self.progress_information:
            logging.info("Stop watch log in %s", host_progress['host'])
            self.remote_operations.open_conn_and_login(host_progress['host'], self.NETACT_DEFAULT_ROOT_USERANME,
                                                       root_password)
            for progress in host_progress['progress']:
                self.remote_operations.execute_command("kill -9 " + progress['progress'])

        logging.info("Stop watch logs done.")

    def download_watched_logs(self, root_password, local_directory_path):
        logging.info("Download logs start.")
        if not self.local_file_operations.check_directory_exist(local_directory_path):
            self.local_file_operations.create_directory(local_directory_path)
        for host_log in self.progress_information:
            logging.info("Down logs in %s", host_log['host'])
            for log in host_log['progress']:
                self.remote_operations.download_file_to_local(host_log['host'], self.NETACT_DEFAULT_ROOT_USERANME,
                                                              root_password, log['log_path'],
                                                              local_directory_path, log['save_name'])
        logging.info("Download logs done.")
