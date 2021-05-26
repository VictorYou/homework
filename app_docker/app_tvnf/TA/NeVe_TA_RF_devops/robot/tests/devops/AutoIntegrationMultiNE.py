# __author__ = 'x5luo'
import logging
import os
import sys
from xml.etree.ElementTree import Element
from IntegrationTools.AutoIntegration.AutoIntegration import AutoIntegration
from oss_radio_tools_lib.Remote.RemoteOperations import RemoteOperations

class AutoIntegrationMultiNE(AutoIntegration):
    def __init__(self, ne_type, remote_operations=None):
        AutoIntegration.__init__(self, ne_type, remote_operations)
        self.TEMPLATE_FILE_PATH = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "Templates" + os.path.sep
        self.REMOTE_TEMPLATE_FILE_PATH = "/var/opt/oss/global/NSN-fsdc/com.nokianetworks.oss.neiw/conf/template/InitializationTemplate/"
        self.WORK_DIR = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "Generation"

    def get_neiw_template_file_name(self, ne_type, ne_version):
        '''ne_type.ne_version.xml = template_name'''
        logging.info("get neiw template file name start.")
#        dns = dn.split("/")
#        integrate_ne_name = dns[len(dns)-1]
#        mo_class = integrate_ne_name.split("-")
#        template_name = mo_class[0].upper() + "." + ne_version.upper() + ".xml"
        template_name = ne_type.strip().upper() + "." + ne_version.strip().upper() + ".xml"
        logging.info("got neiw template file: " + template_name + ".")
        return template_name

    def set_remote_template_file_and_ne_type(self,file_name, ne_type, param_list): #TODO:
        logging.info("Download neiw template file start.")
        if file_name is not None:
            self.TEMPLATE_NAME = file_name
            self.REMOTE_TEMPLATE_FILE_PATH = self.REMOTE_TEMPLATE_FILE_PATH + self.TEMPLATE_NAME
            self.remote_operations.download_file_to_local(param_list["NETACT_HOST"], param_list["OMC_USERNAME"], param_list["OMC_PASSWORD"],
                                                          self.REMOTE_TEMPLATE_FILE_PATH, self.TEMPLATE_FILE_PATH, self.TEMPLATE_NAME)
            self.TEMPLATE_FILE_PATH = self.TEMPLATE_FILE_PATH + self.TEMPLATE_NAME
        if ne_type is not None:
            self.NE_Type = ne_type
        logging.info("Download neiw template file done.")

    def add_MO_to_configure_file(self, tree_xml, DN, HOST_NAME, VERSION):
        logging.info("Add MO information to configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance/MO")
        nodes[0].set("distName", DN + "/NE3SWS-1")
        nodes[1].set("distName", DN + "/EM-1")
        nodes[2].set("distName", DN + "/SCLI-1")

        nodes = tree_xml.findall("NEType/NEInstance/MO/hostName")
        for i in nodes:
            i.text = HOST_NAME
        #nodes[0].text = HOST_NAME
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

    def add_TLS_value_to_configure_file(self, tree_xml, tlsValue):
        logging.info("ADD TLS Mode to configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance/MO/securityMode")
        nodes[0].text=tlsValue
        logging.info("ADD TLS Mode to configure file done.")

    def add_IP_value_to_configure_file(self, tree_xml, ipValue):
        logging.info("ADD IP version to configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance/MO/ipVersion")
        nodes[0].text = ipValue
        logging.info("ADD IP version to configure file done.")


    def generate_NEIW_configure_file(self, param_list):
        logging.info("Generate NEIW configure file start.")


        self.copy_NEIW_configure_file_to_work_directory(param_list["DN"])

        '''Part 1: file parser by XML'''
        tree = self.parse_NEIW_configure_file()
        self.set_MO_version(tree)
        if ("username" in param_list) and ("password" in param_list):
                self.add_user_information_to_configure_file(tree, param_list["username"], param_list["password"])
                param_list.pop("username")  #remove element to reduce time cost on follow string replacement
                param_list.pop("password")
        self.save_NEIW_configure_file(tree)  #must before Part 2
        #TODO: optional parameter in NEIW file generation?
        # if DNS_Server is None:
        #     pass
        # else:
        #     self.add_DNS_NTP_to_configure_file(DNS_Server, NTP_Server, username, password)

        '''Part 2: File parser by String replacement '''
        self.set_param_value_to_configure_file_and_save_file(tree, param_list)

        logging.info("Generate NEIW configure file done. File: %s" % self.WORK_CONFIGURE_FILE_PATH)

    def integrate_NE(self, neiw_param_list):
        logging.info("Integrate NE start.")

        self.remote_operations.open_conn_and_login(neiw_param_list["NETACT_HOST"], neiw_param_list["OMC_USERNAME"], neiw_param_list["OMC_PASSWORD"])

        self.create_MR_object( neiw_param_list["NETACT_LBWAS"], neiw_param_list["OMC_USERNAME"], neiw_param_list["OMC_PASSWORD"], neiw_param_list["MR"] )

        self.generate_NEIW_configure_file(neiw_param_list)


        if neiw_param_list["credentials"] is not None: #TODO: optional action?
            logging.info("*************************Create credential*************************")
            self.create_credential(neiw_param_list["credentials"], neiw_param_list["MR"], neiw_param_list["OMC_USERNAME"], neiw_param_list["OMC_PASSWORD"])

        operation_result = self.execute_integration_operation(neiw_param_list["NETACT_HOST"], neiw_param_list["OMC_USERNAME"], neiw_param_list["OMC_PASSWORD"])
        if operation_result:
            logging.info("Integrate %s successfully!", neiw_param_list["DN"])
        else:
            logging.error("Integrate %s failed.", neiw_param_list["DN"])
        self.remote_operations.close_conn()
        # self.local_file_operations.delete_file(self.WORK_CONFIGURE_FILE_PATH)
        logging.info("Integrate NE done.")
        return operation_result

    def fetch_OMC_password(self, VIIS_HOSTNAME, VIIS_SERVER_USER, VIIS_SERVER_PASSWORRD):
        remote_operations_viss = RemoteOperations()
        remote_operations_viss.open_conn_and_login(VIIS_HOSTNAME, VIIS_SERVER_USER, VIIS_SERVER_PASSWORRD)
        rc = remote_operations_viss.execute_command(
           "/opt/nokia/oss/bin/syscredacc.sh -user omc -type appserv -instance appserv")
        omc_pwd = rc[0].strip()
        remote_operations_viss.close_conn()
        return omc_pwd




if __name__=='__main__':
    #omc_password = auto_integration.fetch_OMC_password("clab478node14.netact.nsn-rdnet.net", "root", "arthur")
    #
    # input_param_list = {
    #                   #"NETACT_HOST": "10.93.143.140",
    #                   #"NETACT_LBWAS": "clab1997lbwas.netact.nsn-rdnet.net",
    #    "NETACT_HOST": "10.91.133.166",
    # #     #"NETACT_HOST": "10.93.109.178",
    #     "NETACT_LBWAS": "sprintlab449lbwas.netact.nsn-rdnet.net",
    #                   "OMC_USERNAME": "omc",
    #                   "OMC_PASSWORD": omc_password,
    #                   "DN": "PLMN-PLMN/CWLC-11381",
    #                   "CWLC address": "10.53.146.166",
    #                   "MR": "MRC-WIFI/MR-WIFI",
    #                   "CWLC distinguished name": "PLMN-PLMN/CWLC-11381",
    #                   "NE3SWS agent security mode": 0,
    #                   "NE3SWS IP version": 0,
    #                   "NE3SWS agent HTTPS connection port": "8059",
    #                   "NE3SWS agent HTTP connection port": "8060",
    #                   "username": "wifi123",
    #                   "password": "wifi123",
    #                   "TLS_MODE": "0",         # 1= TLS, 0 = non-TLS
    #                   "IP_VERSION": "0",      # 1 = IPv6, 0 = IPv4
    #                   "credentials" : { "Web Service Access": {"username": "cwlcadmin", "password": "Ssh4wifi", "group": ['sysop']},
    #                                       "SCLI Access": {"username": "nokadmin", "password": "Nokia123", "group": ['sysop']}
    #                                     }
    #                   }
    input_param_list = {
       "ne_type": "OMS",
       "ne_version": "LOMS18",
       "NETACT_HOST": "10.91.133.166",
#        "NETACT_HOST": "10.93.109.178",
#        "NETACT_HOST": "10.32.214.236",
       "NETACT_LBWAS": "sprintlab449lbwas.netact.nsn-rdnet.net",
        #"NETACT_LBWAS": "clab478lbwas.netact.nsn-rdnet.net",
#        "NETACT_LBWAS": "clab3417bwas.netact.nsn-rdnet.net",
        "OMC_USERNAME": "omc",
        "OMC_PASSWORD": "omc",
        "MR" : "MRC-MRC/MR-OMS",
        #"DN": "PLMN-PLMN/OMS-2125",
        #"OMS O&M agent address": "10.9.221.190",
        #"OMS distinguished name": "PLMN-PLMN/OMS-2058",
        "DN" : "PLMN-PLMN/OMS-2125",
#        "DN": "PLMN-PLMN/OMS-10010",
#        "OMS O&M agent address" : "10.9.142.133",
        "OMS O&amp;M agent address" : "10.9.142.133",
#        "OMS O&M agent address": "10.9.10.124",
        "OMS distinguished name" : "PLMN-PLMN/OMS-2125",
#        "OMS distinguished name": "PLMN-PLMN/OMS-10010",
        #"Configure DNS forwarder in OMS" : "null",
        #"Configure NTP server in OMS" : "null",
        #"OMS root password" : "null",
        "NE presentation name" : "OMS-2125",
#        "NE presentation name": "OMS-10010",
        #"NE presentation name": "OMS-2058",
        "credentials": {"NWI3 Access": {"username": "Nemuadmin", "password": "nemuuser", "group": "sysop"}},
    }
#     input_param_list = {
#         "ne_type": "NOKLTE",
#         "ne_version": "FL19",
#         "NETACT_HOST": "10.32.214.236", # dmgr node ip
#         "NETACT_LBWAS": "clab3417lbwas.netact.nsn-rdnet.net",
#         "DN" : "PLMN-PLMN/MRBTS-801",
#         "OMC_USERNAME": "omc",
#         "OMC_PASSWORD" : "omc",
#         #"OMC_PASSWORD": omc_password,
#         "MR" : "MRC-MRC/MR-BTSMED",
#         "MRBTS address" : "mrbts-801.netact.com",
#         "MRBTS distinguished name" : "PLMN-PLMN/MRBTS-801",
#         "NE3SWS agent security mode" : "0", # 0 = No TLS; 1 = TLS
#         "MRBTS EM address" : "10.93.245.31",
#         #"NE3SWS agent HTTP connection port" : "8080",  # default value
#         "NE3SWS agent HTTPS connection port" : "8443", # default value
#         "IP Version" : "IPV4", #default value 0-IPv4/1-IPv6
#         "credentials" : None,
#     }
    attempts = 0
    success = False


    if not input_param_list.has_key("ne_type"):
        print "ne_type is the necessary parameter, it can't be null."
        exit(1)
    if not input_param_list.has_key("ne_version"):
        print "ne_version is the necessary parameter, it can't be null."
        exit(1)
    if not input_param_list("MR"):
        print "MR is the necessary parameter, it can't be null."
        exit(1)
    if not input_param_list("NETACT_HOST"):
        print "NETACT_HOST is the necessary parameter, it can't be null."
        exit(1)
    if not input_param_list("NETACT_LBWAS"):
        print "NETACT_LBWAS is the necessary parameter, it can't be null."
        exit(1)
    if not input_param_list("credentials"):
        print "credentials is the necessary parameter, it can't be null."
        input_param_list["credentials"] = None

    auto_integration = AutoIntegrationMultiNE(input_param_list["ne_type"])

#    omc_password = auto_integration.fetch_OMC_password("sprintlab449vm20.netact.nsn-rdnet.net", "root", "arthur")
#    input_param_list["OMC_PASSWORD"] = omc_password

    neiw_template_name = auto_integration.get_neiw_template_file_name(input_param_list["ne_type"], input_param_list["ne_version"])

    auto_integration.set_remote_template_file_and_ne_type(neiw_template_name,
                                                           input_param_list["ne_type"],
                                                           input_param_list)  # TODO:  modify according to RTE NEIW template path

    while attempts < 3 and not success:
#        try:
        success = auto_integration.integrate_NE(input_param_list)
#        except:
        attempts += 1
        print "++++++++++++++++++++++++++++++++"
        print attempts
        print "++++++++++++++++++++++++++++++++"
#            if attempts == 3:
#                break
    print "============="
    print success
    print "============="
    if success:
        exit(0)
    else:
        exit(1)

