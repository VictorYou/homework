# __author__ = 'x5luo'
import logging
import os
import sys
from xml.etree.ElementTree import Element
from AutoIntegration import AutoIntegration


class AutoIntegrationOMS(AutoIntegration):
    def __init__(self, remote_operations=None):
        AutoIntegration.__init__(self, 'OMS', remote_operations)
        self.TEMPLATE_NAME = "OMS.xml"
        self.NE_Type = "OMS"
        self.TEMPLATE_FILE_PATH = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "Templates" + os.path.sep + self.TEMPLATE_NAME

    def add_MO_to_configure_file(self, tree_xml, OMS_DN, HOST_NAME, VERSION):
        logging.info("Add MO information to configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance/MO")
        nodes[0].set("distName", OMS_DN + "/HTTP-1")
        nodes = tree_xml.findall("NEType/NEInstance/MO/hostName")
        nodes[0].text = HOST_NAME
        nodes = tree_xml.findall("NEType/NEInstance/MR/MO/version")
        nodes[0].text = VERSION
        nodes = tree_xml.findall("NEType")
        nodes[0].set('version', VERSION)
        logging.info("Add MO information to configure file done.")

    def add_DNS_NTP_to_configure_file(self, tree_xml, DNS_Server, NTP_Server, username, password):
        logging.info("Add DNS and NTP server to configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance")
        nodes[0].set('DNSserver', DNS_Server)
        nodes[0].set('NTPserver', NTP_Server)
        nodes = tree_xml.findall("NEType/NEInstance/userInfos/userInfo/username")
        nodes[0].text = username
        nodes = tree_xml.findall("NEType/NEInstance/userInfos/userInfo/password")
        nodes[0].text = password
        logging.info("Add DNS and NTP server to configure file done.")

    def add_user_information_to_configure_file(self, tree_xml, username, password):
        nodes = tree_xml.findall("NEType/NEInstance")
        userInfos_node = Element('userInfos', {})
        userinfo_node = Element('userInfo', {'type': "SUSSH"})
        username_node = Element('username', {})
        username_node.text = username
        password_node = Element('password', {})
        password_node.text = password
        userinfo_node.append(username_node)
        userinfo_node.append(password_node)
        userInfos_node.append(userinfo_node)
        nodes[0].append(userInfos_node)

    def generate_NEIW_configure_file(self, OMS_DN, HOST_NAME, MR_NAME, VERSION, DNS_Server, NTP_Server, username,
                                     password):
        logging.info("Generate NEIW configure file start.")
        logging.info("template file path: %s", self.TEMPLATE_FILE_PATH)
        self.copy_NEIW_configure_file_to_work_directory(OMS_DN)
        tree = self.parse_NEIW_configure_file()
        self.add_agent_address_to_configure_file(tree, HOST_NAME)
        self.add_MR_to_configure_file(tree, OMS_DN, MR_NAME)
        self.add_MO_to_configure_file(tree, OMS_DN, HOST_NAME, VERSION)
        if username is not None:
            self.add_user_information_to_configure_file(tree, username, password)
        if DNS_Server is None:
            pass
        else:
            self.add_DNS_NTP_to_configure_file(DNS_Server, NTP_Server, username, password)
        self.save_NEIW_configure_file(tree)
        logging.info("Generate NEIW configure file done.")

    def integrate_OMS(self, NETACT_HOST, NETACT_LBWAS,OMC_USERNAME, OMC_PASSWORD, OMS_DN, NE_HOST_NAME, MR_NAME,
                      VERSION=None, DNS_Server=None, NTP_Server=None, username=None, password=None, credentials=None,
                      cm_upload_flag=False):
        logging.info("Integrate OMS start.")
        self.remote_operations.open_conn_and_login(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        self.create_MR_object(NETACT_LBWAS, OMC_USERNAME, OMC_PASSWORD, MR_NAME)
        self.generate_NEIW_configure_file(OMS_DN, NE_HOST_NAME, MR_NAME, VERSION, DNS_Server, NTP_Server, username,
                                          password)
        if credentials is not None:
            logging.info("*************************Create credential*************************")
            self.create_credential(credentials, MR_NAME, OMC_USERNAME, OMC_PASSWORD)
        # self.remote_operations.open_conn_and_login(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        operation_result = self.execute_integration_operation(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        if operation_result:
            logging.info("Integrate %s successfully!", OMS_DN)
            if cm_upload_flag:
                self.do_cm_upload(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD, OMS_DN)
        else:
            logging.error("Integrate %s failed.", OMS_DN)
        self.remote_operations.close_conn()
        self.local_file_operations.delete_file(self.WORK_CONFIGURE_FILE_PATH)
        logging.info("Integrate OMS done.")
        return operation_result


if __name__ == '__main__':
    auto_integration = AutoIntegrationOMS()
    # auto_integration.integrate_OMS(NETACT_HOST="10.91.147.254",OMC_USERNAME= "omc", OMC_PASSWORD="1546--User", OMS_DN="PLMN-PLMN/OMS-401", NE_HOST_NAME="10.62.91.228",
    #                                MR_NAME="MRC-OMS/MR-Radiact", VERSION="WOMS16")
    #auto_integration.integrate_OMS(NETACT_HOST="10.92.21.59", OMC_USERNAME="omc", OMC_PASSWORD="omc", OMS_DN="PLMN-PLMN/OMS-1028", NE_HOST_NAME="10.8.85.207",
     #                              MR_NAME="MRC-OMS/MR-Radiact", VERSION="WOMS16", credentials={
      #      "NWI3 Access": {"username": "Nemuadmin", "password": "nemuuser", "group": "sysop"},
       #     "EM Access": {"username": "Nemuadmin", "password": "nemuuser", "group": "sysop"}})
    # auto_integration.integrate_OMS(NETACT_HOST="10.91.48.42",OMC_USERNAME= "omc", OMC_PASSWORD="1464--User", OMS_DN="PLMN-PLMN/OMS-1028",NE_HOST_NAME= "10.8.85.207",
    #                                 MR_NAME="MRC-OMS/MR-PRIVI", VERSION="WOMS16", credentials={
    #          "NWI3 Access": {"username": "Nemuadmin", "password": "nemuuser", "group": "sysop"}})
	
    auto_integration.integrate_OMS(NETACT_HOST="10.91.133.166", NETACT_LBWAS="sprintlab449lbwas.netact.nsn-rdnet.net",OMC_USERNAME= "omc", OMC_PASSWORD="omc", OMS_DN="PLMN-PLMN/OMS-2125",NE_HOST_NAME= "10.9.142.133",
                                    MR_NAME="MRC-MRC/MR-OMS", VERSION="LOMS18"
                                   , credentials={"NWI3 Access": {"username": "Nemuadmin", "password": "nemuuser", "group": "sysop"}}
                                   )

    # NETACT_HOST = sys.argv[1]
    # NETACT_LBWAS = sys.argv[2]
    # OMC_USERNAME = sys.argv[3]
    # OMC_PASSWORD = sys.argv[4]
    # OMS_DN = sys.argv[5]
    # NE_HOST_NAME = sys.argv[6]
    # MR_NAME = sys.argv[7]
    # NE_VERSION = sys.argv[8]
    # NE_USERNAME = sys.argv[9]
    # NE_PASSWORD = sys.argv[10]
    # CRE_GROUP = sys.argv[11]
    # groups = str(CRE_GROUP).split(',')
    # groups_list = []
    # for g in groups:
    #     groups_list.append(g)
    # operation_result = auto_integration.integrate_OMS(NETACT_HOST,NETACT_LBWAS,OMC_USERNAME, OMC_PASSWORD, OMS_DN,NE_HOST_NAME,MR_NAME, NE_VERSION, credentials={"NWI3 Access": {"username": NE_USERNAME, "password": NE_PASSWORD, "group": groups_list}})
    # if operation_result == False:
    #     sys.exit(1)