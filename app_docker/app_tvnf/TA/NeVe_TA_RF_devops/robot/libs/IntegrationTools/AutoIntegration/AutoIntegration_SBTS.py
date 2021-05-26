# __author__ = 'x5luo'
import logging
import os

from IntegrationTools.AutoIntegration.AutoIntegration import AutoIntegration


class AutoIntegration_SBTS(AutoIntegration):
    def __init__(self, remote_operations=None):
        AutoIntegration.__init__(self, 'SBTS', remote_operations)
        self.TEMPLATE_NAME = "SBTS.xml"
        self.NE_Type = "SBTS"
        self.TEMPLATE_FILE_PATH = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "Templates" + os.path.sep + self.TEMPLATE_NAME

    def add_MO_to_configure_file(self, tree_xml, SBTS_DN, HOST_NAME, HTTP_PORT,
                                 HTTPS_PORT, IP_VERSION, TLS_MODEL, NE_VERSION):
        logging.info("Add MO information to configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance/MO")
        nodes[0].set("distName", SBTS_DN + "/NE3SWS-1")
        nodes = tree_xml.findall("NEType/NEInstance/MO/hostName")
        nodes[0].text = HOST_NAME
        nodes = tree_xml.findall("NEType/NEInstance/MO/httpPort")
        nodes[0].text = HTTP_PORT
        nodes = tree_xml.findall("NEType/NEInstance/MO/httpsPort")
        nodes[0].text = HTTPS_PORT
        nodes = tree_xml.findall("NEType/NEInstance/MO/ipVersion")
        nodes[0].text = self.get_ip_version_value(IP_VERSION)
        nodes = tree_xml.findall("NEType/NEInstance/MO/securityMode")
        nodes[0].text = self.get_tls_value(TLS_MODEL)
        nodes = tree_xml.findall("NEType/NEInstance/MR/MO/version")
        nodes[0].text = NE_VERSION
        logging.info("Add MO information to configure file done.")

    # def add_NEAC_credential_to_configure_file(self, tree_xml, credentials):
    #     logging.info("Add NEAC credential to configure file start.")
    #     credentials_element = Element("credentials", {"class": "SBTS"})
    #     for key, value in credentials.items():
    #         credential_element = Element("credential", {"type": key, "group": value['group']})
    #         username_element = Element("username")
    #         username_element.text = value['username']
    #         password_element = Element("password")
    #         password_element.text = value['password']
    #         credential_element.append(username_element)
    #         credential_element.append(password_element)
    #         credentials_element.append(credential_element)
    #     nodes = tree_xml.findall("NEType/NEInstance")
    #     nodes[0].append(credentials_element)
    #     logging.info("Add NEAC credential to configure file done.")

    def generate_NEIW_configure_file(self, SBTS_DN, HOST_NAME, MR_NAME, NE_Version, HTTP_PORT,
                                     HTTPS_PORT, IP_VERSION, TLS_MODEL):
        logging.info("Generate NEIW configure file start.")
        self.copy_NEIW_configure_file_to_work_directory(SBTS_DN)
        tree = self.parse_NEIW_configure_file()
        self.add_agent_address_to_configure_file(tree, HOST_NAME)
        self.add_MR_to_configure_file(tree, SBTS_DN, MR_NAME)
        self.add_MO_to_configure_file(tree, SBTS_DN, HOST_NAME, HTTP_PORT, HTTPS_PORT, IP_VERSION, TLS_MODEL,
                                      NE_Version)
        # if credentials != None:
        #     self.add_NEAC_credential_to_configure_file(tree, credentials)
        self.save_NEIW_configure_file(tree)
        logging.info("Generate NEIW configure file done.")

    def check_precondition(self, netact_host, tls_model):
        logging.info("Check pre-condition start.")
        if int(self.get_tls_value(tls_model)) == 1:
            std_output, std_errors = self.remote_operations.execute_command_ignore_error(
                'wget --no-check-certificate https://' + netact_host + ":8443/NE3SRegistrationService")
            print std_output
            print "Error:"
            print std_errors
        else:
            std_output, std_errors = self.remote_operations.execute_command_ignore_error(
                'wget http://' + netact_host + ':8443/NE3SRegistrationService')
            pass
        logging.info("Check pre-condition done.")

    def integrate_SBTS(self, NETACT_HOST, OMC_USERNAME, OMC_PASSWORD, SBTS_DN, NE_HOST_NAME, MR_NAME,
                       NE_VERSION="SBTS16.2", HTTP_PORT="8080", HTTPS_PORT="8443", IP_VERSION="ipv4", TLS_MODEL="notls",
                       credentials=None, cm_upload_flag=False):
        logging.info("Integrate SBTS start.")
        self.remote_operations.open_conn_and_login(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        # self.check_precondition(NE_HOST_NAME, TLS_MODEL)
        self.create_MR_object(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD, MR_NAME)
        self.generate_NEIW_configure_file(SBTS_DN, NE_HOST_NAME, MR_NAME, NE_VERSION, HTTP_PORT,
                                          HTTPS_PORT, IP_VERSION, TLS_MODEL)
        if credentials is not None:
            logging.info("*************************Create credential*************************")
            self.create_credential(credentials, MR_NAME, OMC_USERNAME, OMC_PASSWORD)
        self.remote_operations.open_conn_and_login(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        operation_result = self.execute_integration_operation(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        if operation_result:
            logging.info("Integrate %s successfully!", SBTS_DN)
            if cm_upload_flag:
                self.do_cm_upload(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD, SBTS_DN)
        else:
            logging.error("Integrate %s failed.", SBTS_DN)
        self.remote_operations.close_conn()
        self.local_file_operations.delete_file(self.WORK_CONFIGURE_FILE_PATH)
        logging.info("Integrate SBTS done.")
        return operation_result


if __name__ == '__main__':
    auto_integration = AutoIntegration_SBTS()
    # auto_integration.integrate_SBTS(NETACT_HOST="10.91.147.254", OMC_USERNAME="omc", OMC_PASSWORD="1546--User", SBTS_DN="PLMN-PLMN/SBTS-1771",
    #                                 NE_HOST_NAME="10.91.227.159", MR_NAME="MRC-SBTS/MR-Radiact", NE_VERSION="SBTS16.2", TLS_MODEL="tls",
    #                                 cm_upload_flag=True)
    # auto_integration.integrate_SBTS(NETACT_HOST="10.91.114.44", OMC_USERNAME="omc", OMC_PASSWORD="753--User",
    #                                 SBTS_DN="PLMN-PLMN/SBTS-2665",
    #                                 NE_HOST_NAME="10.69.232.28", MR_NAME="MRC-SBTS/MR-keane", NE_VERSION="SBTS16.2",
    #                                 TLS_MODEL="no-tls",
    #                                 credentials={"Web Service Access": {
    #                                     "username": "sbtsoam", "password": "A0zY~rP#8Mx@", "group": "sysop"}})
    auto_integration.integrate_SBTS(NETACT_HOST="10.92.71.76",OMC_USERNAME= "omc", OMC_PASSWORD="omc", SBTS_DN="PLMN-PLMN/SBTS-1771",
                                    NE_HOST_NAME="10.91.227.159", MR_NAME="MRC-SBTS/MR-Radiact", NE_VERSION="SBTS16.10",
                                    TLS_MODEL="no-tls",
                                    credentials={"Web Service Access": {
                                        "username": "sbtsoam", "password": "A0zY~rP#8Mx@",
                                        "group": "sysop"}})
    # auto_integration.integrate_SBTS(NETACT_HOST="10.91.116.80", OMC_USERNAME="omc", OMC_PASSWORD="1421--User",
    #                                 SBTS_DN="PLMN-PLMN/SBTS-1779",
    #                                 NE_HOST_NAME="10.91.227.148", MR_NAME="MRC-SBTS/MR-keane", NE_VERSION="SBTS16.2",
    #                                 TLS_MODEL="Tls",
    #                                 credentials={"Web Service Access": {
    #                                     "username": "sbtsoam", "password": "A0zY~rP#8Mx@", "group": "sysop"}})
    # auto_integration.integrate_SBTS(NETACT_HOST="10.91.147.254", OMC_USERNAME="omc", OMC_PASSWORD="1546--User",
    #                                 SBTS_DN="PLMN-PLMN/SBTS-1779",
    #                                 NE_HOST_NAME="10.91.227.148", MR_NAME="MRC-SBTS/MR-keane", NE_VERSION="SBTS16.2",
    #                                 TLS_MODEL="Tls",
    #                                 credentials={"Web Service Access": {
    #                                     "username": "sbtsoam", "password": "A0zY~rP#8Mx@", "group": "sysop"}})

    # auto_integration.integrate_SBTS(NETACT_HOST="10.91.86.234", OMC_USERNAME="omc", OMC_PASSWORD="0025--User",
    #                                 SBTS_DN="PLMN-PLMN/SBTS-15",
    #                                 NE_HOST_NAME="10.58.251.225", MR_NAME="MRC-SBTS/MR-testCnmu", NE_VERSION="SBTS16.10",
    #                                 TLS_MODEL="no-Tls",
    #                                 credentials={"Web Service Access": {
    #                                     "username": "sbtsoam", "password": "A0zY~rP#8Mx@", "group": "sysop"}})
    # auto_integration.integrate_SBTS(NETACT_HOST="10.91.116.80",OMC_USERNAME= "omc", OMC_PASSWORD="1421--User", SBTS_DN="PLMN-PLMN/SBTS-15",
    #                                  NE_HOST_NAME="10.58.251.225", MR_NAME="MRC-SBTS/MR-Radiact_keane", NE_VERSION="SBTS16.10",
    #                                  TLS_MODEL="no-tls",
    #                                  credentials={"Web Service Access": {
    #                                      "username": "sbtsoam", "password": "A0zY~rP#8Mx@",
    #                                      "group": "sysop"}})