import Integration_Workflow_Info_BTSMED as IWI
from AutoConfigure_BTSMED import Configure_BTSMED
from AutoIntegration_BTSMED import AutoIntegrate_BTSMED
from AutoUpgradeBTSMED import Upgrade_BTSMED
from InstallCertificate.InstallNetActCertificate_NEW import InstallNetActCertificate
from ConfigureMultipleNEDNS import ConfigureNEDNS
from oss_radio_tools_lib.Remote import RemoteOperations
import logging


class Start_Workflow(object):
    def __init__(self):
        loglevel = IWI.loglevel
        if loglevel == "INFO":
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename='Integration_Workflow_BTSMED.log',
                                filemode='w')
        if loglevel == "CRITICAL":
            logging.basicConfig(level=logging.CRITICAL,
                                format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename='Integration_Workflow_BTSMED.log',
                                filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        self.remoteOperations = RemoteOperations.RemoteOperations()

    def check_BTSMED_configue_file(self):
        if IWI.TLS_MODEL.lower() == 'tls' and IWI.tlsModeNorthbound.lower() == 'forced':
            logging.critical("Will start TLS integration for BTSMED")
            # else:
            #     logging.info("Conflict detected, please check TLS_MODEL of NetAct Infor and tlsModeNorthbound for BTSMED Infor, they should be consistent")
            #     exit()
        elif IWI.TLS_MODEL.lower() == 'notls' and IWI.tlsModeNorthbound.lower() == 'off':
            logging.critical("Will start none-tls integration for BTSMED")
        elif IWI.TLS_MODEL.lower() != '' and IWI.tlsModeNorthbound.lower() != '':
            logging.error("Conflict detected, please check TLS_MODEL of NetAct Infor and tlsModeNorthbound for BTSMED Infor, they should be consistent")
            exit()
            # else:
            #     logging.info("Conflict detected, please check TLS_MODEL of NetAct Infor and tlsModeNorthbound for BTSMED Infor, they should be consistent")
            #     exit()

        if IWI.Upgrade_BTSMED and IWI.New_BTSMED_rpm_link != '':
            logging.critical("Will upgrade BTSMED")
            # print "upgrade"
        elif IWI.Upgrade_BTSMED == False:
            logging.critical("Keep BTSMED current version")
        else:
            logging.error("Have to provide NEW RPM download link if Upgrade_BTSMED is True")
            exit()

    def check_ads_deploy(self):
        if IWI.Integrate_BTSMED:
            logging.critical("Checking ADS deployment for " + IWI.NE_VERSION)
            self.remoteOperations.open_conn_and_login(IWI.NETACT_WAS_IP,IWI.OMC_USERNAME,IWI.OMC_PASSWORD)
            result = self.remoteOperations.execute_command("ls /d/oss/global/var/adaptations/o2ml | grep " + IWI.NE_VERSION + "$")
            self.remoteOperations.close_conn()
            if len(result) == 0:
                logging.critical("The adaptation for " + IWI.NE_VERSION + " is not deployed. Please deploy the adaptation first")
                exit()
            else:
                logging.critical("The adaptation for " + IWI.NE_VERSION + " is deployed. Continue integration.")

    def autoconfigBTSMED(self):
        if IWI.Reconfigure_BTSMED:
            logging.critical("Configure BTSMED Start")
            self.ACB = Configure_BTSMED(IWI.NE_Type)
            self.ACB.Auto_Configure_BTSMED(IWI.NE_VERSION, IWI.dnsIPAddress, IWI.northboundGateway, IWI.northboundIpAddress, IWI.southboundGateway, IWI.southboundIpAddress, IWI.tlsModeNorthbound, IWI.BTSMED_ROOT_USER, IWI.BTSMED_ROOT_PWD, IWI.NE_Type,IWI.caSubjectName,IWI.cmpPreSharedKey,IWI.cmpRefNum,IWI.serverHost,IWI.serverPort,IWI.init_id)
            logging.critical("Configure BTSMED Done")
        else:
            logging.critical("Configure BTSMED -- Skipped")

    def autoUpgrade(self):
        if IWI.Upgrade_BTSMED:
            logging.critical("Upgrade BTSMED Start")
            self.UB = Upgrade_BTSMED()
            self.UB.upgradeBTSMED(IWI.northboundIpAddress, IWI.New_BTSMED_rpm_link, IWI.BTSMED_ROOT_USER, IWI.BTSMED_ROOT_PWD)
            logging.critical("Upgrade BTSMED Done")
        else:
            logging.critical("Upgrade BTSMED -- Skipped")

    def autoIntegBTSMED(self):
        if IWI.Integrate_BTSMED:
            logging.critical("Integrate BTSMED Start")
            self.AIB = AutoIntegrate_BTSMED()
            integration_result = self.AIB.integrate_BTSMED(IWI.NETACT_WAS_IP, IWI.NETACT_LBWAS, IWI.OMC_USERNAME, IWI.OMC_PASSWORD, IWI.BTSMED_DN, IWI.NE_HOST_NAME, IWI.MR_NAME, IWI.NE_VERSION, IWI.HTTP_PORT, IWI.HTTPS_PORT,IWI.IP_VERSION, IWI.TLS_MODEL, IWI.credentials, IWI.cm_upload_flag)
            if integration_result:
                logging.critical("Integrate BTSMED Successfully")
            else:
                logging.critical("Integrate BTSMED Failed")
        else:
            logging.critical("Integrate BTSMED -- Skipped")

    def autoInstallCert(self):
        if IWI.Install_NetAct_Certificate:
            logging.critical("Install certificate to NetAct Start")
            self.INC = InstallNetActCertificate()
            self.INC.install_certificate(IWI.NETACT_WAS_IP, IWI.NetAct_ROOT_PWD, IWI.serverHost, IWI.ca_id_of_CA)
            logging.critical("Install certificate to NetAct Done")
        else:
            logging.critical("Install certificate to NetAct -- Skipped")

    def autoConfigureDNS(self):
        if IWI.Confiure_DNS:
            logging.critical("Configure DNS Start")
            self.CNDS = ConfigureNEDNS()
            domain_name_dict = {}
            domain_name_dict[IWI.NE_HOST_NAME] = IWI.northboundIpAddress
            self.CNDS.configure_network_elements_dns(domain_name_dict,IWI.NETACT_WAS_IP, IWI.OMC_USERNAME, IWI.OMC_PASSWORD, IWI.NetAct_ROOT_PWD)
            logging.critical("Configure DNS Done")
        else:
            logging.critical("Configure DNS -- Skipped")

    def workflow_process(self):
        self.check_BTSMED_configue_file()
        self.check_ads_deploy()
        self.autoUpgrade()
        self.autoconfigBTSMED()
        self.autoConfigureDNS()
        self.autoInstallCert()
        self.autoIntegBTSMED()

if __name__ == '__main__':
    SW = Start_Workflow()
    # print IWI.init_id
    # SW.check_ads_deploy()
    # SW.workflow_process()
    # SW.check_BTSMED_configue_file()
    SW.autoconfigBTSMED()