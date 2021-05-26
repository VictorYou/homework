from oss_radio_tools_lib.Remote.RemoteOperations import RemoteOperations
from oss_radio_tools_lib.Remote.LocalFileOperations import LocalFileOperations
import logging
import paramiko
import os
import time


class Configure_BTSMED(object):
    Configure_Command_INIT = "sh Configure_BTSMED_INIT.sh"
    Configure_Command_RESTART = "sh Configure_BTSMED_RESTART.sh"
    Configure_Command_STATUS = "sh Configure_BTSMED_STATUS.sh"
    Configure_Command_SETUP = "sh Configure_BTSMED_SETUP.sh"
    Configure_Command_CMP = "sh Configure_BTSMED_CMP.sh"
    Check_Port_Comand = "netstat -tanup | grep "
    def __init__(self, NE_Type, remote_operations=None):
        if remote_operations is None:
            self.remote_operations = RemoteOperations()
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename='AutoConfigure' + NE_Type + '.log',
                                filemode='w')
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
        else:
            self.remote_operations = remote_operations
        self.TEMPLATE_FILE_PATH = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__))) + os.path.sep + "Templates" + os.path.sep

    def Upload_BTSMED_Configure_File(self,BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD, FileName):
        TEMPLATE_NAME = FileName + ".sh"
        CONFIGURE_FILE_PATH = self.TEMPLATE_FILE_PATH + TEMPLATE_NAME
        Remote_configure_file_path = "/home/" + BTSMED_ROOT_USER + "/" + TEMPLATE_NAME
        # print self.CONFIGURE_FILE_PATH
        # print Remote_configure_file_path
        self.remote_operations.upload_file_to_remote(BTSMED_IP, BTSMED_ROOT_USER, BTSMED_ROOT_PWD,
                                                     CONFIGURE_FILE_PATH, Remote_configure_file_path)

    def Execute_Init(self,BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD, init_id):
        self.Upload_BTSMED_Configure_File(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD,"Configure_BTSMED_INIT")
        self.remote_operations.open_conn_and_login(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD)
        logging.info("Initialize BTSMED configuration start.")
        self.remote_operations.execute_command("sed -i \'/init_id/s/init_id/" + str(init_id) + "/g\' Configure_BTSMED_INIT.sh")
        result = self.remote_operations.execute_command(self.Configure_Command_INIT)
        logging.info(result)
        logging.info("Initialize BTSMED configuration done.")
        self.remote_operations.close_conn()

    def Execute_Restart(self,BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD):
        self.Upload_BTSMED_Configure_File(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD,"Configure_BTSMED_RESTART")
        self.remote_operations.open_conn_and_login(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD)
        logging.info("Restart BTSMED start.")
        result = self.remote_operations.execute_command(self.Configure_Command_RESTART)
        logging.info(result)
        logging.info("Restart BTSMED done.")
        self.remote_operations.close_conn()

    def Execute_Status(self,BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD):
        self.Upload_BTSMED_Configure_File(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD,"Configure_BTSMED_STATUS")
        self.remote_operations.open_conn_and_login(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD)
        logging.info("Check status of BTSMED start.")
        for i in range(20):
            result = self.remote_operations.execute_command(self.Configure_Command_STATUS)
            logging.info(result)
            if ["btsmedProcess state: started; \n" , "groupDaemonProcess state: started; \n" , "redisProcess state: started ; \n"] == result:
                logging.info("BTSMED is ready")
                break
            else:
                logging.info("BTSMED is NOT ready")
                time.sleep(10)
                if i == 19:
                    logging.info("BTSMED is not ready in 200 seconds. Please check.")
                    exit()
                else:
                    continue
        logging.info("Check status of BTSMED done.")
        self.remote_operations.close_conn()

    def Execute_Setup(self,BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD,dnsIPAddress,northboundGateway,northboundIpAddress,southboundGateway,southboundIpAddress,tlsModeNorthbound,BTSMED_VERSION):
        ne_list = ['BTSMED17A','BTSMED18']
        if BTSMED_VERSION in ne_list:
            self.Create_Setup_file(dnsIPAddress,northboundGateway,northboundIpAddress,southboundGateway,southboundIpAddress,tlsModeNorthbound)
        else:
            self.Create_Setup_file_18SP(dnsIPAddress,northboundGateway,northboundIpAddress,southboundGateway,southboundIpAddress,tlsModeNorthbound)
        self.Upload_BTSMED_Configure_File(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD,"Configure_BTSMED_SETUP")
        self.remote_operations.open_conn_and_login(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD)
        logging.info("Setup BTSMED configuration start.")
        result = self.remote_operations.execute_command(self.Configure_Command_SETUP)
        logging.info(result)
        logging.info("Setup BTSMED configuration done.")
        self.remote_operations.close_conn()

    def Check_Port(self,BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD,tlsModeNorthbound):
        if tlsModeNorthbound.lower() == 'off':
            port = '8080'
        elif tlsModeNorthbound.lower() == 'forced':
            port = '8443'
        self.remote_operations.open_conn_and_login(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD)
        logging.info("Check BTSMED port start.")
        self.Check_Port_Comand = self.Check_Port_Comand + port
        for i in range(20):
            result = self.remote_operations.execute_command(self.Check_Port_Comand)
            logging.info(result)
            if result != [] and result[0].find("LISTEN") and result[0].find(BTSMED_IP):
                logging.info("BTSMED is listening " + port)
                logging.info("BTSMED is setup successfully")
                break
            else:
                logging.info("BTSMED is NOT listening " + port)
                time.sleep(10)
                if i == 19:
                    logging.info("BTSMED is not listening " + port + " in 200 seconds. Please check.")
                    exit()
                else:
                    continue
        logging.info("Check BTSMED port done.")
        self.remote_operations.close_conn()

    def Create_Setup_file(self,dnsIPAddress,northboundGateway,northboundIpAddress,southboundGateway,southboundIpAddress,tlsModeNorthbound):
        if tlsModeNorthbound.lower() == 'off':
            tlsModeNorthbound = 'Off'
        elif tlsModeNorthbound.lower() == 'forced':
            tlsModeNorthbound = 'Forced'
        Setup_file_path = self.TEMPLATE_FILE_PATH + 'Configure_BTSMED_SETUP.sh'
        Setup_file = open(Setup_file_path,'wb')
        Setup_Content = ''
        Setup_Content += "#!/bin/bash\n"
        Setup_Content += "echo \"==========Configuring BTSMED==========\"\n"
        Setup_Content += "/usr/bin/expect <<-EOF\n"
        Setup_Content += "spawn sudo -u Nemuadmin /opt/imp/`rpm -qa | grep nokia | cut -d \"-\" -f 3`/cli/bin/imp-cli-control.sh start\n"
        Setup_Content += "expect \"btsmed>\"\n"
        Setup_Content += "send \"config set --dn /BTSMED-1\\r\"\n"
        Setup_Content += "expect \"*dnsIPAddress:\"\n"
        Setup_Content += "send \"" + dnsIPAddress + "\\r\"\n"
        Setup_Content += "expect \"*northboundGateway:\"\n"
        Setup_Content += "send \"" + northboundGateway + "\\r\"\n"
        Setup_Content += "expect \"*northboundIpAddress:\"\n"
        Setup_Content += "send \"" + northboundIpAddress + "\\r\"\n"
        Setup_Content += "expect \"*northboundIpPrefixLength:\"\n"
        Setup_Content += "send \"20\\r\"\n"
        Setup_Content += "expect \"*ntpIPAddress1:\"\n"
        Setup_Content += "send \"" + dnsIPAddress + "\\r\"\n"
        Setup_Content += "expect \"*ntpIPAddress2:\"\n"
        Setup_Content += "send \"" + dnsIPAddress + "\\r\"\n"
        Setup_Content += "expect \"*ntpIPAddress3:\"\n"
        Setup_Content += "send \"" + dnsIPAddress + "\\r\"\n"
        Setup_Content += "expect \"*southboundGateway:\"\n"
        Setup_Content += "send \"" + southboundGateway + "\\r\"\n"
        Setup_Content += "expect \"*southboundIpAddress:\"\n"
        Setup_Content += "send \"" + southboundIpAddress + "\\r\"\n"
        Setup_Content += "expect \"*southboundIpPrefixLength:\"\n"
        Setup_Content += "send \"20\\r\"\n"
        Setup_Content += "expect \"*timeZone:\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"*tlsModeNorthbound:\"\n"
        Setup_Content += "send \"" + tlsModeNorthbound + "\\r\"\n"
        Setup_Content += "expect \"*tlsModeSouthbound:\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"btsmed>\"\n"
        Setup_Content += "send \"config commit\\r\"\n"
        Setup_Content += "expect \"*(y/n)\"\n"
        Setup_Content += "send \"y\\r\"\n"
        Setup_Content += "expect eof\n"
        Setup_Content += "EOF"
        Setup_file.write(Setup_Content)
        Setup_file.close()

    def Create_Setup_file_18SP(self,dnsIPAddress,northboundIpv4Gateway,northboundIpv4Address,southboundIpv4Gateway,southboundIpv4Address,tlsModeNorthbound):
        if tlsModeNorthbound.lower() == 'off':
            tlsModeNorthbound = 'Off'
        elif tlsModeNorthbound.lower() == 'forced':
            tlsModeNorthbound = 'Forced'
        Setup_file_path = self.TEMPLATE_FILE_PATH + 'Configure_BTSMED_SETUP.sh'
        Setup_file = open(Setup_file_path,'wb')
        Setup_Content = ''
        Setup_Content += "#!/bin/bash\n"
        Setup_Content += "echo \"==========Configuring BTSMED==========\"\n"
        Setup_Content += "/usr/bin/expect <<-EOF\n"
        Setup_Content += "spawn sudo -u Nemuadmin /opt/imp/`rpm -qa | grep nokia | cut -d \"-\" -f 3`/cli/bin/imp-cli-control.sh start\n"
        Setup_Content += "set timeout 120\n"
        Setup_Content += "expect \"btsmed>\"\n"
        Setup_Content += "send \"config set --dn /BTSMED-1\\r\"\n"
        Setup_Content += "expect \"*dnsIPAddress>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b" + dnsIPAddress + "\\r\"\n"
        Setup_Content += "expect \"*northboundIpv4Address>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b" + northboundIpv4Address + "\\r\"\n"
        Setup_Content += "expect \"*northboundIpv4Gateway>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b" + northboundIpv4Gateway + "\\r\"\n"
        Setup_Content += "expect \"*northboundIpv4PrefixLength>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b20\\r\"\n"
        Setup_Content += "expect \"*northboundIpv6Address>\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"*northboundIpv6Gateway>\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"*northboundIpv6PrefixLength>\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"*ntpIPAddress1>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b" + dnsIPAddress + "\\r\"\n"
        Setup_Content += "expect \"*ntpIPAddress2>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b" + dnsIPAddress + "\\r\"\n"
        Setup_Content += "expect \"*ntpIPAddress3>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b" + dnsIPAddress + "\\r\"\n"
        Setup_Content += "expect \"*southboundIpv4Address>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b" + southboundIpv4Address + "\\r\"\n"
        Setup_Content += "expect \"*southboundIpv4Gateway>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b\\b" + southboundIpv4Gateway + "\\r\"\n"
        Setup_Content += "expect \"*southboundIpv4PrefixLength>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b20\\r\"\n"
        Setup_Content += "expect \"*southboundIpv6Address>\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"*southboundIpv6Gateway>\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"*southboundIpv6PrefixLength>\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"*timeZone>\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"*tlsModeNorthbound>\"\n"
        Setup_Content += "send \"\\b\\b\\b\\b\\b\\b" + tlsModeNorthbound + "\\r\"\n"
        Setup_Content += "expect \"*tlsModeSouthbound>\"\n"
        Setup_Content += "send \"\\r\"\n"
        Setup_Content += "expect \"(y/n)\"\n"
        Setup_Content += "send \"y\\r\"\n"
        Setup_Content += "expect \"btsmed>\"\n"
        Setup_Content += "send \"exit\\r\"\n"
        Setup_Content += "expect eof\n"
        Setup_Content += "EOF"
        Setup_file.write(Setup_Content)
        Setup_file.close()

    def Create_CMP_file(self,caSubjectName,cmpPreSharedKey,cmpRefNum,serverHost,serverPort):
        CMP_file_path = self.TEMPLATE_FILE_PATH + 'Configure_BTSMED_CMP.sh'
        CMP_file = open(CMP_file_path,'wb')
        CMP_Content = ''
        CMP_Content += "#!/bin/bash\n"
        CMP_Content += "echo \"==========Configuring BTSMED CMP==========\"\n"
        CMP_Content += "/usr/bin/expect <<-EOF\n"
        CMP_Content += "spawn sudo -u Nemuadmin /opt/imp/`rpm -qa | grep nokia | cut -d \"-\" -f 3`/cli/bin/imp-cli-control.sh start\n"
        CMP_Content += "expect \"btsmed>\"\n"
        CMP_Content += "send \"config set --dn /BTSMED-1/CERTH-1/CMP-1\\r\"\n"
        CMP_Content += "expect \"*caCertificateUpdateTime:\"\n"
        CMP_Content += "send \"15\\r\"\n"
        CMP_Content += "expect \"*caSubjectName:\"\n"
        CMP_Content += "send \"" + caSubjectName + "\\r\"\n"
        CMP_Content += "expect \"*cmpPreSharedKey:\"\n"
        CMP_Content += "send \"" + cmpPreSharedKey + "\\r\"\n"
        CMP_Content += "expect \"*cmpRefNum:\"\n"
        CMP_Content += "send \"" + cmpRefNum + "\\r\"\n"
        CMP_Content += "expect \"*eeSubjectName:\"\n"
        CMP_Content += "send \"O=Nokia,CN=BTSMED\\r\"\n"
        CMP_Content += "expect \"*neCertificateUpdateTime:\"\n"
        CMP_Content += "send \"15\\r\"\n"
        CMP_Content += "expect \"*serverHost:\"\n"
        CMP_Content += "send \"" + serverHost + "\\r\"\n"
        CMP_Content += "expect \"*serverPath:\"\n"
        CMP_Content += "send \"pkix\\r\"\n"
        CMP_Content += "expect \"*serverPort:\"\n"
        CMP_Content += "send \"" + serverPort + "\\r\"\n"
        CMP_Content += "expect \"btsmed>\"\n"
        CMP_Content += "send \"config commit\\r\"\n"
        CMP_Content += "expect \"btsmed>\"\n"
        CMP_Content += "send \"cmp initialize\\r\"\n"
        CMP_Content += "expect \"btsmed>\"\n"
        CMP_Content += "send \"config list --dn /BTSMED-1/CERTH-1/CMP-1\\r\"\n"
        CMP_Content += "expect \"btsmed>\"\n"
        CMP_Content += "send \"exit\\r\"\n"
        CMP_Content += "expect eof\n"
        CMP_Content += "EOF"
        CMP_file.write(CMP_Content)
        CMP_file.close()

    def Execute_cmp(self,BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD,caSubjectName,cmpPreSharedKey,cmpRefNum,serverHost,serverPort):
        self.Create_CMP_file(caSubjectName,cmpPreSharedKey,cmpRefNum,serverHost,serverPort)
        self.Upload_BTSMED_Configure_File(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD,"Configure_BTSMED_CMP")
        self.remote_operations.open_conn_and_login(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD)
        logging.info("Setup BTSMED CMP configuration start.")
        result = self.remote_operations.execute_command(self.Configure_Command_CMP)
        logging.info(result)
        if '  state: CMP_InitializationOK\r\n' in result:
            logging.info("Configure CMP for BTSMED successfully")
        else:
            logging.info("Configure CMP for BTSMED Failed")
        logging.info("Setup BTSMED CMP configuration done.")
        self.remote_operations.close_conn()

    def Auto_Configure_BTSMED(self,BTSMED_VERSION,dnsIPAddress,northboundGateway,northboundIpAddress,southboundGateway,southboundIpAddress,tlsModeNorthbound,BTSMED_ROOT_USER='toor4nsn',BTSMED_ROOT_PWD='oZPS0POrRieRtu',NE_Type='BTSMED',caSubjectName="C=CN, O=NOKIA, CN=CA_NETACT_TEST_TLS",cmpPreSharedKey="6kA8-4nD7-bzVB-Qq8s",cmpRefNum="9558",serverHost="10.91.83.136",serverPort="8081",init_id='1'):
        self.Execute_Init(northboundIpAddress,BTSMED_ROOT_USER, BTSMED_ROOT_PWD, init_id)
        self.Execute_Restart(northboundIpAddress,BTSMED_ROOT_USER, BTSMED_ROOT_PWD)
        self.Execute_Status(northboundIpAddress,BTSMED_ROOT_USER, BTSMED_ROOT_PWD)
        ne_list = ['BTSMED17A','BTSMED18']
        self.Execute_Setup(northboundIpAddress,BTSMED_ROOT_USER, BTSMED_ROOT_PWD,dnsIPAddress,northboundGateway,northboundIpAddress,southboundGateway,southboundIpAddress,tlsModeNorthbound,BTSMED_VERSION)
        self.Check_Port(northboundIpAddress,BTSMED_ROOT_USER, BTSMED_ROOT_PWD,tlsModeNorthbound)
        if tlsModeNorthbound.lower() == 'forced':
            self.Execute_cmp(northboundIpAddress,BTSMED_ROOT_USER, BTSMED_ROOT_PWD,caSubjectName,cmpPreSharedKey,cmpRefNum,serverHost,serverPort)


if __name__ == '__main__':
    ACB = Configure_BTSMED('BTSMED')
    # ACB.Execute_Init('10.91.82.200','toor4nsn','oZPS0POrRieRtu','555')
    # ACB.Execute_Restart('10.91.85.17','toor4nsn','oZPS0POrRieRtu')
    # ACB.Execute_Status('10.91.85.17','toor4nsn','oZPS0POrRieRtu')
    # ACB.Execute_Setup('10.91.85.17','toor4nsn','oZPS0POrRieRtu')
    # ACB.Check_Port('10.91.85.17','toor4nsn','oZPS0POrRieRtu','8080')
    # ACB.Auto_Configure_BTSMED(dnsIPAddress='10.91.84.117',northboundGateway='10.91.80.1',northboundIpAddress='10.91.85.17',southboundGateway='10.91.112.1',southboundIpAddress='10.91.113.2',tlsModeNorthbound='Forced')
    # ACB.Execute_cmp('10.91.85.17','toor4nsn','oZPS0POrRieRtu',caSubjectName="C=CN, O=NOKIA, CN=CA_NETACT_TEST_TLS",cmpPreSharedKey="6kA8-4nD7-bzVB-Qq8s",cmpRefNum="9558",serverHost="10.91.83.136",serverPort="8081")
    # ACB.Auto_Configure_BTSMED(dnsIPAddress='10.91.33.79',northboundGateway='10.91.32.1',northboundIpAddress='10.91.39.56',southboundGateway='10.92.64.1',southboundIpAddress='10.92.72.64',tlsModeNorthbound='Off')
    # ACB.Auto_Configure_BTSMED(dnsIPAddress='10.91.114.70',northboundGateway='10.91.32.1',northboundIpAddress='10.91.39.56',southboundGateway='10.92.64.1',southboundIpAddress='10.92.72.64',tlsModeNorthbound='Off')
    # ACB.Auto_Configure_BTSMED(dnsIPAddress='10.92.20.122',northboundGateway='10.92.16.1',northboundIpAddress='10.92.22.171',southboundGateway='10.91.144.1',southboundIpAddress='10.91.152.15',tlsModeNorthbound='Forced',BTSMED_ROOT_PWD='Monday123!')
    ACB.Create_Setup_file_18SP(dnsIPAddress='10.91.114.70',northboundIpv4Gateway='10.91.32.1',northboundIpv4Address='10.91.39.56',southboundIpv4Gateway='10.92.64.1',southboundIpv4Address='10.92.72.64',tlsModeNorthbound='Off')