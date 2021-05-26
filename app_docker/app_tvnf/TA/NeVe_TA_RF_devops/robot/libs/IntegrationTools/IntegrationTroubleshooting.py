# __author__ = 'x5luo'

import sys
import os
from IntegrationTools.AutoIntegration.AutoIntegration_OMS import AutoIntegration_OMS

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '../Lib/NetAct'))

import logging
from IntegrationTools.AutoIntegration.AutoIntegration_SBTS import AutoIntegration_SBTS
from Troubleshooting.LogOperations import LogOperations
from Troubleshooting.CheckIntegrationLog import CheckIntegrationLog
from oss_radio_tools_lib.Remote.RemoteOperations import RemoteOperations


class IntegrationTroubleshooting(object):
    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='AutoIntegration_Troubleshooting.log',
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        self.remote_operations = RemoteOperations()
        self.log_operations = LogOperations(self.remote_operations)
        self.auto_integration = AutoIntegration_SBTS(self.remote_operations)
        self.check_integration_log = CheckIntegrationLog()

    def open_mediation_trace_log(self, root_password):
        logging.info("Open mediation trace log start.")
        self.log_operations.open_common_mediation_trace_log(root_password)
        self.log_operations.open_gep_mediation_trace_log(root_password)
        logging.info("Open mediation trace log done.")

    def close_mediation_trace_log(self, root_password):
        logging.info("Close mediation trace log start.")
        self.log_operations.close_common_mediation_trace_log(root_password)
        self.log_operations.close_gep_mediation_trace_log(root_password)
        logging.info("Close mediation trace log done.")


if __name__ == "__main__":
    NETACT_HOST = "10.91.147.254"
    NETACT_ROOT_PASSWORD = "arthur"
    NETACT_OMC_USERNAME = "omc"
    NETACT_OMC_PASSWORD = "omc"
    SBTS_DN = "PLMN-PLMN/SBTS-1771"
    SBTS_HOST = "10.56.99.85"
    MR_DN = "MRC-SBTS/MR-Radiact_keane"
    TLS_MODEL = "no-tls"
    NE_VERSION = "SBTS16.2"
    NEAC = {"Web Service Access": {
    "username": "sbtsoam", "password": "A0zY~rP#8Mx@", "group": "sysop"}}
    troubleshooting = IntegrationTroubleshooting()
    troubleshooting.remote_operations.open_conn_and_login(NETACT_HOST, "root", NETACT_ROOT_PASSWORD)
    troubleshooting.open_mediation_trace_log(NETACT_ROOT_PASSWORD)
    troubleshooting.log_operations.start_watch_log(NETACT_ROOT_PASSWORD)
    try:
    # get was node.!!!! not release
        operation_result = troubleshooting.auto_integration.integrate_SBTS(NETACT_HOST,
                                                                       NETACT_OMC_USERNAME,
                                                                       NETACT_OMC_PASSWORD,
                                                                       SBTS_DN, SBTS_HOST, MR_DN, NE_VERSION=NE_VERSION,
                                                                       TLS_MODEL=TLS_MODEL)
    # print operation_result
    finally:
        troubleshooting.log_operations.stop_watch_logs(NETACT_ROOT_PASSWORD)
        troubleshooting.log_operations.download_watched_logs(NETACT_ROOT_PASSWORD,
                                                         "C:/Users/kshao/Project_Tools/oss_radiact_tools/IntegrationTools/AutoIntegration_Troubleshooting_logs/logs/")
        troubleshooting.close_mediation_trace_log(NETACT_ROOT_PASSWORD)
        troubleshooting.remote_operations.close_conn()
        troubleshooting.check_integration_log.check_integration_logs(SBTS_DN, SBTS_HOST,
                                                                 "C:/Users/kshao/Project_Tools/oss_radiact_tools/IntegrationTools/AutoIntegration_Troubleshooting_logs/logs/")
        pass
# auto_oms = AutoIntegration_OMS()
# auto_oms.test()
