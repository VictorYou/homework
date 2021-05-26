# __author__ = 'x5luo'
import logging
import os

from IntegrationTools.AutoIntegration.AutoIntegration import AutoIntegration


class AutoIntegration_BSC(AutoIntegration):
    def __init__(self, remote_operations=None):
        AutoIntegration.__init__(self, 'BSC', remote_operations)
        self.TEMPLATE_NAME = "BSC.xml"
        self.NE_Type = "BSC"
        self.TEMPLATE_FILE_PATH = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "Templates" + os.path.sep + self.TEMPLATE_NAME

    def add_MO_to_configure_file(self, tree_xml, BSC_DN, VERSION, agentInterface):
        logging.info("Add MO information to configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance/MO")
        nodes[0].set("distName", BSC_DN + "/OSI-1")
        nodes = tree_xml.findall("NEType/NEInstance/MR/MO/version")
        nodes[0].text = VERSION
        nodes = tree_xml.findall("NEType")
        nodes[0].set('version', VERSION)
        nodes = tree_xml.findall("NEType/NEInstance/MR/MO/AgentInterface")
        nodes[0].text = agentInterface
        logging.info("Add MO information to configure file done.")

    def add_user_information_to_configure_file(self, tree_xml, username, password):
        logging.info("Add user information to configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance/userInfos/userInfo/username")
        nodes[0].text = username
        nodes = tree_xml.findall("NEType/NEInstance/userInfos/userInfo/password")
        nodes[0].text = password
        logging.info("Add user information to configure file done.")

    def generate_NEIW_configure_file(self, BSC_DN, HOST_NAME, MR_NAME, VERSION, AgentInterface, username, password):
        logging.info("Generate NEIW configure file start.")
        self.copy_NEIW_configure_file_to_work_directory(BSC_DN)
        tree = self.parse_NEIW_configure_file()
        self.add_agent_address_to_configure_file(tree, HOST_NAME)
        self.add_MR_to_configure_file(tree, BSC_DN, MR_NAME)
        self.add_MO_to_configure_file(tree, BSC_DN, VERSION, AgentInterface)
        self.add_user_information_to_configure_file(tree, username, password)
        self.save_NEIW_configure_file(tree)
        logging.info("Generate NEIW configure file done.")

    def integrate_BSC(self, NETACT_HOST, OMC_USERNAME, OMC_PASSWORD, BSC_DN, NE_HOST_NAME, MR_NAME,
                      VERSION=None, username="SYSTEM", password="SYSTEM", credentials=None,
                      AgentInterface="TELNET", cm_upload_flag=False):
        logging.info("Integrate BSC start.")
        self.remote_operations.open_conn_and_login(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        self.create_MR_object(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD, MR_NAME)
        self.generate_NEIW_configure_file(BSC_DN, NE_HOST_NAME, MR_NAME, VERSION, AgentInterface, username, password)
        if credentials is not None:
            logging.info("*************************Create credential*************************")
            self.create_credential(credentials, MR_NAME, OMC_USERNAME, OMC_PASSWORD)
        self.remote_operations.open_conn_and_login(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        operation_result = self.execute_integration_operation(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        if operation_result:
            logging.info("Integrate %s successfully!", BSC_DN)
            if cm_upload_flag:
                self.do_cm_upload(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD, BSC_DN)
        else:
            logging.error("Integrate %s failed.", BSC_DN)
        self.remote_operations.close_conn()
        self.local_file_operations.delete_file(self.WORK_CONFIGURE_FILE_PATH)
        logging.info("Integrate BSC done.")
        return operation_result


if __name__ == '__main__':
    auto_integration = AutoIntegration_BSC()
    # "NEUM Admin Access": {"username": "SYSTEM", "password": "SYSTEM",
    #                   "group": "sysop"}
    # auto_integration.integrate_BSC(NETACT_HOST="10.91.147.254", OMC_USERNAME="omc", OMC_PASSWORD="1546--User",
    #                                BSC_DN="PLMN-PLMN/BSC-12345",
    #                                NE_HOST_NAME="10.58.248.36", MR_NAME="MRC-BSC/MR-Radiact", VERSION="S16_3",
    #                                AgentInterface="TELNET")
    # auto_integration.integrate_BSC(NETACT_HOST="10.91.116.80", OMC_USERNAME="omc", OMC_PASSWORD="1421--User",
    #                                BSC_DN="PLMN-PLMN/BSC-12345",
    #                                NE_HOST_NAME="10.58.248.36",
    #                                MR_NAME="MRC-BSC/MR-Radiact", VERSION="S16_3", AgentInterface='TELNET', credentials={
    #         "Default Access": {"username": "BSCADM", "password": "SYSTEM", "group": ["sysop", "SBTSint"]},
    #         'NEUM Admin Access': {'username': 'SYSTEM', 'password': 'SYSTEM', "group": ["sysop", "SBTSint"]}})
    auto_integration.integrate_BSC(NETACT_HOST="10.92.106.209",OMC_USERNAME= "omc", OMC_PASSWORD="omc",BSC_DN= "PLMN-PLMN/BSC-12345",
                                   NE_HOST_NAME="10.58.248.36",
                                   MR_NAME="MRC-BSC/MR-Radiact", VERSION="S16_3", AgentInterface="TELNET", credentials={
                                "Default Access": {"username": "BSCADM", "password": "SYSTEM","group": "sysop"},
                                'NEUM Admin Access': {'username': 'SYSTEM', 'password': 'SYSTEM', 'group': 'sysop'}})
    # BSC-12345
    # NUPADM
    # PASSWORD
