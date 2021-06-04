# __author__ = 'x5luo'
import logging
import os
import sys
import re
import shutil
import HTMLParser
from xml.etree.ElementTree import ElementTree

from CMUploadTool.CMUploadTool import CMUploadTool
from LocalFileOperations import LocalFileOperations
from RemoteOperations import RemoteOperations
from NEAC.CredTestToolCodeDetails import CredTestToolCodeDetails
from NEAC.NEACInformation import NEACInformation
from NasdaAccess import NasdaOperations
from NetActServiceQuery import NetActServiceQuery


# sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '../../Lib/NetAct'))


class AutoIntegration(object):
    WORK_CONFIGURE_FILE_PATH = ""
    CREATE_CREDENTIAL_SCRIPT_PATH = "/opt/oss/NSN-neac-testsupport/bin/CredTestTool"
    NEIW_GENERATE_CONFIGURE_FILE_COMMAND = "/opt/oss/NSN-AutoIntegrationFramework/Perl-5.14/bin/perl /opt/oss/NSN-AutoIntegrationFramework/bin/ConfGenerator.pl "
    NEIW_AUTOMATICAL_INTEGRATION_COMMAND = "/opt/oss/NSN-AutoIntegrationFramework/Perl-5.14/bin/perl /opt/oss/NSN-AutoIntegrationFramework/bin/AutoIntegrator.pl "
    SWM_config_file = "/opt/oss/NSN-common_mediations/smx/mf-conf/mf-ne3soap.properties"

    def __init__(self, NE_Type, remote_operations=None):
        if remote_operations is None:
            self.remote_operations = RemoteOperations()
            self.html_parser = HTMLParser.HTMLParser()
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename='AutoIntegration_' + NE_Type + '.log',
                                filemode='w')
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
        else:
            self.remote_operations = remote_operations
        self.local_file_operations = LocalFileOperations()
        self.neac_information = NEACInformation()
        self.cred_test_tool_code_details = CredTestToolCodeDetails()
        self.nasda_operations = None
        self.WORK_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "work"
        self.TEMPLATE_FILE_PATH = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "Templates" + os.path.sep
        self.TEMPLATE_NAME = ""
        self.NE_Type = ""
        self.netactservicequery = NetActServiceQuery(self.remote_operations)

    def get_create_objects(self, mr_dn):
        logging.info("Get create objects start.")
        dns = mr_dn.split("/")
        current_dn = None
        create_objects = []
        for dn in dns:
            if current_dn is None:
                current_dn = dn
            else:
                current_dn = current_dn + "/" + dn
            if not self.nasda_operations.check_MOs_exist([current_dn], False):
                create_objects.append(current_dn)
        if len(create_objects) > int(0):
            logging.info("Create objects: ")
            logging.info(create_objects)
        logging.info("Get create objects done.")
        return create_objects

    def create_MR_object(self, hostname, username, password, mr_dn):
        logging.info("Create MR object start.")
        self.nasda_operations = NasdaOperations(hostname, username, password)
        create_objects = self.get_create_objects(mr_dn)
        if len(create_objects) > int(0):
            self.nasda_operations.create_objects(create_objects, True)
        logging.info("Create MR object done.")

    def check_template_file_exist(self):
        logging.info("Check template file exist start.")
        if not self.local_file_operations.check_file_exist(self.TEMPLATE_FILE_PATH):
            raise AssertionError("The template file not exist: %s" % self.TEMPLATE_FILE_PATH)
        logging.info("Check template file exist done.")

    def copy_NEIW_configure_file_to_work_directory(self, dn):
        logging.info("Copy NEIW configure file to work directory start." + self.TEMPLATE_FILE_PATH)
        if not self.local_file_operations.check_directory_exist(self.WORK_DIR):
            self.local_file_operations.create_directory(self.WORK_DIR)
        self.check_template_file_exist()
        self.WORK_CONFIGURE_FILE_PATH = self.WORK_DIR + "/" + dn.replace("/",
                                                                         "%2F") + ".xml"  # TODO: parameterize by input NE
        shutil.copy(self.TEMPLATE_FILE_PATH, self.WORK_CONFIGURE_FILE_PATH)
        logging.info("Copy NEIW configure file to work directory done." + self.WORK_CONFIGURE_FILE_PATH)

    def parse_NEIW_configure_file(self):
        logging.info("Parse NEIW configure xml file start.")
        tree = ElementTree()
        tree.parse(self.WORK_CONFIGURE_FILE_PATH)
        logging.info("Parse NEIW configure xml file done.")
        return tree

    def save_NEIW_configure_file(self, tree_xml):
        logging.info("Save NEIW configure file start.")
        tree_xml.write(self.WORK_CONFIGURE_FILE_PATH, encoding="utf-8", xml_declaration=True)
        logging.info("Save NEIW configure file done.")

    def add_agent_address_to_configure_file(self, tree_xml, host_name):
        logging.info("Add agent to configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance")
        nodes[0].set("agentAddress", host_name)
        logging.info("Add agent to configure file done.")

    def add_MR_to_configure_file(self, tree_xml, BSC_DN, MR_NAME):
        logging.info("Add MR to NEIW configure file start.")
        nodes = tree_xml.findall("NEType/NEInstance/MR")
        nodes[0].set("distName", MR_NAME)
        nodes = tree_xml.findall("NEType/NEInstance/MR/MO")
        nodes[0].set("distName", BSC_DN)
        logging.info("Add MR to NEIW configure file one.")

    def get_ip_version_value(self, IP_VERSION):
        if IP_VERSION.lower() == "ipv6":
            return "1"
        return "0"

    def get_tls_value(self, TLS_MODEL):
        if TLS_MODEL.lower() == "tls":
            return "1"
        return "0"

    def get_create_credential_command(self, service_name, service_parameters_name, service_parameters_value, MR_NAME,
                                      OMC_USERNAME,
                                      OMC_PASSWORD, USER_GROUP):
        logging.info("Get create credential command start.")
        group_parameters = self.get_group_parameters(USER_GROUP)
        command = self.CREATE_CREDENTIAL_SCRIPT_PATH + " -u " + OMC_USERNAME + " -p " + OMC_PASSWORD + " -c -t MR " + \
                  " -s '" + service_name + "' -n '" + MR_NAME + "' " + group_parameters + " -r Default " + " -a " + \
                  service_parameters_name['username'] + " -l '" + service_parameters_value['username'] + "' -a " + \
                  service_parameters_name['password'] + " -l '" + service_parameters_value['password'] + "'"
        logging.info("Get create credential command done.")
        return command

    def check_credential_exist(self, MR_NAME, SERVICE_NAME, OMC_USERNAME, OMC_PASSWORD):
        logging.info("Check %s credential exist start.", SERVICE_NAME)
        command = self.CREATE_CREDENTIAL_SCRIPT_PATH + " -u " + OMC_USERNAME + " -p " + OMC_PASSWORD + " -x | grep '" + SERVICE_NAME + "' |grep " + MR_NAME + ", | wc -l"
        result = self.remote_operations.execute_command(command)
        exist = False
        if int(result[0]) > int(0):
            exist = True
        logging.info("Check %s credential exist done.", SERVICE_NAME)
        return exist

    def delete_credential(self, MR_NAME, SERVICE_NAME, OMC_USERNAME, OMC_PASSWORD):
        logging.info("Delete %s credential start.", SERVICE_NAME)
        command = self.CREATE_CREDENTIAL_SCRIPT_PATH + " -u " + OMC_USERNAME + " -p " + OMC_PASSWORD + " -d -t MR  -s '" + SERVICE_NAME + "' -n '" + MR_NAME + "' -r Default;echo $?"
        result = self.remote_operations.execute_command(command)
        if self.cred_test_tool_code_details.errors[int(result[-1])] != "OK":
            logging.error("Delete Credential failed:")
            logging.error(self.cred_test_tool_code_details.errors[int(result[-1])])
            raise AssertionError("Delete credential failed.")
        logging.info("Delete %s credential done.", SERVICE_NAME)

    def get_group_parameters(self, groups):
        logging.info("Get group parameters start.")
        result = ''
        if isinstance(groups, list):
            for group in groups:
                result += " -g '" + group + "'"
        else:
            result += " -g '" + groups + "' "
        logging.info("Get group parameters done.")
        return result

    def create_credential(self, credentials, MR_NAME, OMC_USERNAME, OMC_PASSWORD):
        logging.info("Create credential start.")
        for key, service_parameters_value in credentials.items():
            if self.check_credential_exist(MR_NAME, key, OMC_USERNAME, OMC_PASSWORD):
                logging.info("The credential %s exist, delete exist credential", key)
                self.delete_credential(MR_NAME, key, OMC_USERNAME, OMC_PASSWORD)
            service_parameters_name = self.neac_information.get_service_information(key)
            create_credential_command = self.get_create_credential_command(key, service_parameters_name,
                                                                           service_parameters_value, MR_NAME,
                                                                           OMC_USERNAME, OMC_PASSWORD,
                                                                           service_parameters_value[
                                                                               'group']) + ";echo $?"
            result = self.remote_operations.execute_command(create_credential_command)
            result_code = result[-1]
            if self.cred_test_tool_code_details.errors[int(result_code)] != "OK":
                logging.error("Create Credential failed:")
                logging.error(self.cred_test_tool_code_details.errors[int(result_code)])
                # raise AssertionError("Create Credential failed")
        logging.info("Create credential done.")

    def recover_MANIFEST_file_permission(self):
        if self.remote_operations.check_file_exist(
                "/opt/WebSphere/AppClient/configuration/org.eclipse.osgi/bundles/42/data/com.ibm.ws.runtime.mqjms/META-INF/MANIFEST.MF"):
            self.remote_operations.execute_command(
                "chown omc  /opt/WebSphere/AppClient/configuration/org.eclipse.osgi/bundles/42/data/com.ibm.ws.runtime.mqjms/META-INF/MANIFEST.MF")

    def do_cm_upload(self, netact_host, omc_username, omc_password, dn):
        logging.info("Do CM Upload for " + dn + " start.")
        cm_upload = CMUploadTool(netact_host, omc_username, omc_password, remote_operations=self.remote_operations)
        cm_upload.do_cm_upload_for_single_element(dn)
        logging.info("Do CM Upload for " + dn + " done.")

    def execute_integration_operation(self, NETACT_HOST, OMC_USERNAME, OMC_PASSWORD):
        logging.info("Execute integration operation start.")
        tar_get_configure_file_path = "/var/tmp/" + self.NE_Type + "_" + OMC_USERNAME + ".xml"
        final_configure_file_path = "/var/tmp/" + self.NE_Type + "_" + OMC_USERNAME + "_final.xml"
        self.remote_operations.upload_file_to_remote(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD,
                                                     self.WORK_CONFIGURE_FILE_PATH, tar_get_configure_file_path)
        self.recover_MANIFEST_file_permission()
        result = self.remote_operations.execute_command(
            self.NEIW_GENERATE_CONFIGURE_FILE_COMMAND + " " + tar_get_configure_file_path + " " + final_configure_file_path)
        # print result
        # print self.NEIW_GENERATE_CONFIGURE_FILE_COMMAND + " " + tar_get_configure_file_path + " " + final_configure_file_path
        logging.info(result)
        result = self.remote_operations.execute_command(
            self.NEIW_AUTOMATICAL_INTEGRATION_COMMAND + " " + final_configure_file_path + " -pcv")
        is_successful = False
        print "Final:"
        print result
        if result[len(result) - 1].find("Successful") != int(-1):
            is_successful = True
        else:
            logging.info("Details information: ")
            logging.error(str(result[0]))
            log_file_path = (str(result[0]).split(":"))[1]
            log_file_path.strip("\n")
            log_content = self.remote_operations.execute_command('cat %s' % log_file_path)
            logging.error("Detail log contents: \n %s" % log_content)
        logging.info("Execute integration operation done.")
        return is_successful

    def execute_integration_operation_BTSMED(self, NETACT_HOST, OMC_USERNAME, OMC_PASSWORD):
        logging.info("Execute integration operation start.")
        final_configure_file_path = "/var/tmp/" + self.NE_Type + "_" + OMC_USERNAME + "_final.xml"
        self.remote_operations.upload_file_to_remote(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD,
                                                     self.WORK_CONFIGURE_FILE_PATH, final_configure_file_path)
        self.recover_MANIFEST_file_permission()
        # print result
        # print self.NEIW_GENERATE_CONFIGURE_FILE_COMMAND + " " + tar_get_configure_file_path + " " + final_configure_file_path
        result = self.remote_operations.execute_command(
            self.NEIW_AUTOMATICAL_INTEGRATION_COMMAND + " " + final_configure_file_path + " -pcv")
        is_successful = False
        print "Final:"
        print result
        if result[len(result) - 1].find("Successful") != int(-1):
            is_successful = True
        else:
            logging.info("Details information: ")
            logging.error(str(result[0]))
        logging.info("Execute integration operation done.")
        return is_successful

    def configure_swm_tls(self, NETACT_HOST, OMC_USERNAME, OMC_PASSWORD, NEType, TLS_MODE):
        logging.info("Configure SWM tls mode start.")
        self.remote_operations.open_conn_and_login(NETACT_HOST, OMC_USERNAME, OMC_PASSWORD)
        dict_host = self.netactservicequery.get_server_ip('common_mediations')
        self.remote_operations.close_conn()
        for value in dict_host.values():
            self.remote_operations.open_conn_and_login(value, OMC_USERNAME, OMC_PASSWORD)
            current_property = self.remote_operations.execute_command(
                'cat ' + self.SWM_config_file + ' | grep com.nsn.mediation.ne3sws.swm.tls.enable.network.element')
            print current_property
            NEstring = current_property[0].strip().split('=')[-1]
            if len(NEstring) != 0:
                NElist = NEstring.split(',')
                if TLS_MODE.lower() == 'forced' or TLS_MODE.lower() == 'tls':
                    if NEType in NElist:
                        continue
                    else:
                        NElist.append(NEType)
                        NElist_new_string = ','.join(NElist)
                        self.remote_operations.execute_command(
                            'sed -i \'/com.nsn.mediation.ne3sws.swm.tls.enable.network.element/s/' + NEstring + '/' + NElist_new_string + '/g\' ' + self.SWM_config_file)
                elif TLS_MODE.lower() == 'off' or TLS_MODE.lower() == 'no-tls' or TLS_MODE.lower() == 'notls':
                    if NEType in NElist:
                        NElist.remove(NEType)
                        NElist_new_string = ','.join(NElist)
                        self.remote_operations.execute_command(
                            'sed -i \'/com.nsn.mediation.ne3sws.swm.tls.enable.network.element/s/' + NEstring + '/' + NElist_new_string + '/g\' ' + self.SWM_config_file)
            else:
                if TLS_MODE.lower() == 'forced':
                    self.remote_operations.execute_command(
                        'sed -i \'/com.nsn.mediation.ne3sws.swm.tls.enable.network.element/s/com.nsn.mediation.ne3sws.swm.tls.enable.network.element=/com.nsn.mediation.ne3sws.swm.tls.enable.network.element=' + NEType + '/g\' ' + self.SWM_config_file)
                else:
                    continue
            after_property = self.remote_operations.execute_command(
                'cat ' + self.SWM_config_file + ' | grep com.nsn.mediation.ne3sws.swm.tls.enable.network.element')
            print after_property
            self.remote_operations.close_conn()
        logging.info("Configure SWM tls mode done.")

    def set_param_value_to_configure_file_and_save_file(self, tree_xml, dict_params):
        logging.info("Set Key field  with Value in configure file, start.")
        nodes = tree_xml.find("./NEType/parameters")
        dict_replace = {}

        '''Process default value firstly'''
        for item in nodes:
            if item.attrib.has_key('default'):
                dict_replace[item.attrib['id']] = item.attrib['default']

        '''Create dict with parameter_id:value, like #1#: 10.10.10.10'''
        for eachName in dict_params.keys():
            # Process special character.
            pattern_of_special_character = r'(&\w+;)'
            find_special_character = re.search(pattern_of_special_character, eachName)
            if find_special_character:
                tmp_value = dict_params[eachName]
                eachName = self.html_parser.unescape(eachName)
                dict_params[eachName] = tmp_value

            for item in nodes:
                if item.attrib['name'] == eachName:
                    dict_replace[item.attrib['id']] = dict_params[eachName]
                    break
                else:
                    continue

        enumlist = []
        mappingValue = []
        actualValue = []
        for item in nodes:
            '''Process ENUM type parameters.'''
            is_enum_type_exit = re.search(r'(ENUM:)', item.attrib['type'])
            if is_enum_type_exit:
                enumlist = item.attrib['type'].split(':')
                mappingValue = enumlist[1].split('/')
                #print "input " + dict_replace[item.attrib['id']].upper()
                valueHash = {}

                for each in mappingValue:
                    actualValue = each.split('-')
                    #Convert ENUM:0-IPv4/1-IPv6 X to {'1': 'IPv6', '0': 'IPv4'}
                    valueHash[actualValue[0]] = actualValue[1]
                for key in valueHash.keys():
                    if key.upper() == dict_replace[item.attrib['id']].upper() or valueHash[key].upper() == dict_replace[item.attrib['id']].upper():
                        dict_replace[item.attrib['id']] = key

                if valueHash.has_key(dict_replace[item.attrib['id']]):
                    pass
                else:
                    logging.error(item.attrib['name']  + " = " + dict_replace[
                        item.attrib['id']] + " is not correct. It must be " + str(valueHash))
                    exit(1)

            is_number_type_exist = re.search(r'(^NUMBER$)', item.attrib['type'])
            if is_number_type_exist:
                #print item.attrib['name'] + " = " + dict_replace[item.attrib['id']]
                is_number = re.search(r'(^[0-9]{1,5}$)', dict_replace[item.attrib['id']])
                if is_number:
                    pass
                else:
                    logging.error(item.attrib['name'] + " = " + dict_replace[
                        item.attrib['id']] + " is not correct. It must be NUMBER.")
                    exit(1)

            is_fqdn_type_exit = re.search(r'(^FQDN$)', item.attrib['type'])
            if is_fqdn_type_exit:
                pattern = r''+ item.attrib['validateExpression'] +''
                is_fqdn = re.search(pattern, dict_replace[item.attrib['id']])
                if is_fqdn:
                    pass
                else:
                    logging.error(item.attrib['name'] + " = " + dict_replace[
                        item.attrib['id']] + " is not correct. It must like " + item.attrib['validateExpression'])
                    exit(1)

        if len(dict_replace) > 0:
            rc = self.replace_all_parameter_id_with_value(self.WORK_CONFIGURE_FILE_PATH, dict_replace)
            return rc
        else:
            logging.info("Warning: no parameter_id  in configure file set  value.")
            return False
        logging.info("Set Key field  with Value in configure file, end.")

    def replace_all_parameter_id_with_value(self, file, dict_replace_id):
        if os.path.exists("%s.bak" % file):
            os.remove("%s.bak" % file)

        with open(file, "r") as f1, open("%s.bak" % file, "w") as f2:
            for line in f1:
                # TODO: emunate list data and replace
                for eachID in dict_replace_id.keys():
                    if eachID in line:
                        print eachID, dict_replace_id[eachID]
                        line = line.replace(eachID, str(dict_replace_id[eachID]))
                        continue  # Can be 'break' when single repacement in single line
                    else:
                        pass  # NOT continue
                f2.write(line)
            f1.close()
            f2.close()
        os.remove(file)
        os.rename("%s.bak" % file, file)
        logging.info("Replace remained patterns with null value")
        pattern = r'#\d+#'
        with open(file, "rb") as temp_file:
            content = temp_file.read()
        with open(file, "wb") as temp_file:
            content = re.sub(pattern, "null", content)
            temp_file.write(content)

        return True


    def set_MO_version(self, tree_xml):
        logging.info("Set MO version in configure file start.")
        source_node = tree_xml.find('NEType')
        version_str = source_node.get('version')

        logging.info("Set MO version: %s." % version_str)
        target_node = tree_xml.find('NEType/NEInstance/MR/MO/version')
        target_node.text = version_str
        logging.info("Set MO version in configure file end.")


if __name__ == '__main__':
    ai = AutoIntegration('')
    ai.configure_swm_tls('10.91.81.14', 'omc', 'omc', 'SBTS', 'forced')