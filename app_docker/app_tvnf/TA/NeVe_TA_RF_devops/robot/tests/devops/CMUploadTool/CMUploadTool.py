import logging

from oss_radio_tools_lib.Remote.RemoteOperations import RemoteOperations


class CMUploadTool(object):
    CM_UPLOAD_COMMAND = "racclimx.sh -op Upload "

    def __init__(self, was_host, omc_username, omc_password, remote_operations=None):
        if remote_operations is None:
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename='CMUpload.log',
                                filemode='w')
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
            self.remote_operations = RemoteOperations()
            self.remote_operations.open_conn_and_login(was_host, omc_username, omc_password)
        else:
            self.remote_operations = remote_operations

    def get_additional_parameter(self, dn):
        logging.info("Get additional parameter for " + dn + " start.")
        if "SBTS" in dn:
            parameter = " -sranBtsContentInUse true "
        elif "OMS" in dn or "RNC" in dn or "BSC" in dn:
            parameter = " -btsContentInUse true"
        else:
            raise AssertionError("Unsupported NE type.")
        logging.info("Get additional parameter: " + parameter)
        logging.info("Get additional parameter for " + dn + " doen.")
        return parameter

    def do_cm_upload_for_single_element(self, distinct_name):
        logging.info("Do CM Upload for " + distinct_name + " start.")
        feedback = self.remote_operations.execute_command(
            self.CM_UPLOAD_COMMAND + " -DN " + distinct_name + self.get_additional_parameter(distinct_name))
        if len(feedback) != 0 and feedback != '':
            logging.error(distinct_name + " CM upload failed.")
            logging.error("Command result: " + str(feedback))
            raise AssertionError("CM Upload failed, feedback:" + str(feedback))
        else:
            logging.info(distinct_name + " CMUpload successfully.")

        logging.info("Do CM Upload for " + distinct_name + " done.")

    def do_cm_upload_for_element_robot(self, ne_information):
        logging.info("Do CM Upload for element start.")
        self.do_cm_upload_for_single_element(ne_information['DN'])
        logging.info("Do CM Upload for element done.")

    def do_cm_upload_for_elements(self, distinct_name_list):
        logging.info("Do CM Upload for elements start.")
        for distinct_name in distinct_name_list:
            self.do_cm_upload_for_single_element(distinct_name)
        logging.info("Do CM Upload for elements done.")

    def check_and_do_cm_upload_for_elements_robot(self, ne_list):
        logging.info("Do CM Upload for elements start.")
        for ne in ne_list:
            if ne['CMUpload']:
                self.do_cm_upload_for_single_element(ne['DN'])
        logging.info("Do CM Upload for elements done.")


if __name__ == '__main__':
    cm_upload_tool = CMUploadTool('10.91.114.44', 'omc', 'omc')
    cm_upload_tool.do_cm_upload_for_single_element('PLMN-PLMN/SBTS-1779')
    # LabHost = raw_input("Please input the NetAct node IP:")
    # username = raw_input("Please input the username of NetAct:")
    # password = raw_input("Please input the password of NetAct:")
    # dn_name = raw_input("Please input the Object DN(e.g. PLMN-PLMN/SBTS-15):")
    # cm_upload_tool = CMUploadTool(LabHost, username, password)
    # cm_upload_tool.do_cm_upload_for_single_element(dn_name)
