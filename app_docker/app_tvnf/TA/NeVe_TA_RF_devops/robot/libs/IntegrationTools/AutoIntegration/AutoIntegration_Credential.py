import logging

from oss_radio_tools_lib.NetAct.NEAC.CredTestToolCodeDetails import CredTestToolCodeDetails
from oss_radio_tools_lib.NetAct.NEAC.NEACInformation import NEACInformation
from oss_radio_tools_lib.NetAct.NasdaAccess import NasdaOperations
from oss_radio_tools_lib.Remote.RemoteOperations import RemoteOperations


class AutoIntegration_Credential(object):
    CREATE_CREDENTIAL_SCRIPT_PATH = "/opt/oss/NSN-neac-testsupport/bin/CredTestTool"

    def __init__(self, host, omc_username, omc_password):
        self.remote_operations = RemoteOperations()
        self.remote_operations.open_conn_and_login(host, omc_username, omc_password)
        self.neac_information = NEACInformation()
        self.cred_test_tool_code_details = CredTestToolCodeDetails()
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='AutoIntegration_credential.log',
                            filemode='w')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def close_connection(self):
        self.remote_operations.close_conn()

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

    def check_credential_exist(self, MR_NAME, SERVICE_NAME, OMC_USERNAME, OMC_PASSWORD):
        logging.info("Check %s credential exist start.", SERVICE_NAME)
        command = self.CREATE_CREDENTIAL_SCRIPT_PATH + " -u " + OMC_USERNAME + " -p " + OMC_PASSWORD + " -x | grep '" + SERVICE_NAME + "' |grep " + MR_NAME + " | wc -l"
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
                result += " -g " + group
        else:
            result += " -g " + groups
        logging.info("Get group parameters done.")
        return result

    def create_credential(self, omc_username, omc_password, user_group, type, mr_dn, username,
                          password):
        logging.info("Convert credential start.")
        if self.check_credential_exist(mr_dn, type, omc_username, omc_password):
            self.delete_credential(mr_dn, type, omc_username, omc_password)
        service_parameters_name = self.neac_information.get_service_information(type)
        group_parameters = self.get_group_parameters(user_group)
        create_credential_command = self.CREATE_CREDENTIAL_SCRIPT_PATH + " -u " + omc_username + " -p " + omc_password + " -c -t MR " + \
                                    " -s '" + type + "' -n '" + mr_dn + "' " + group_parameters + " -r Default " + " -a " + \
                                    service_parameters_name['username'] + " -l '" + username + "' -a " + \
                                    service_parameters_name['password'] + " -l '" + password + "' ;echo $?"
        result = self.remote_operations.execute_command(create_credential_command)
        result_code = result[-1]
        if self.cred_test_tool_code_details.errors[int(result_code)] != "OK":
            logging.error("Create Credential failed:")
            logging.error(self.cred_test_tool_code_details.errors[int(result_code)])
            raise AssertionError("Create credential failed.")
        logging.info("Create credential done.")


if __name__ == "__main__":
    create_credential = AutoIntegration_Credential("10.91.116.80", "omc", "1421--User")
    create_credential.create_credential("omc", "1421--User", ["sysop", "SBTSint"], "Web Service Access",
                                        "MRC-SBTS/MR-Radiact_Xin",
                                        "sbtsoam", "A0zY~rP#8Mx@")
