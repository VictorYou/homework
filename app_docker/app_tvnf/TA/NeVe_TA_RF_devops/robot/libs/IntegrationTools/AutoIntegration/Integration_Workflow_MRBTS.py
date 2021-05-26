import Integration_Workflow_Info_MRBTS as IWI
from InstallCertificate.InstallNetActCertificate_NEW import InstallNetActCertificate
from ConfigureMultipleNEDNS import ConfigureNEDNS
from AutoIntegration_SBTS17A import AutoIntegration_MRBTS
from oss_radio_tools_lib.Remote import RemoteOperations
import logging


class Start_Workflow_MRBTS(object):
    def __init__(self):
        loglevel = IWI.loglevel
        if loglevel == "INFO":
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename='Integration_Workflow_MRBTS.log',
                                filemode='w')
        if loglevel == "CRITICAL":
            logging.basicConfig(level=logging.CRITICAL,
                                format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename='Integration_Workflow_MRBTS.log',
                                filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        self.remoteOperations = RemoteOperations.RemoteOperations()

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

    def check_connectivity(self):
        if IWI.Integrate_MRBTS:
            logging.critical("Checking connectivity between BTSMED southbound and MRBTS Start")
            self.remoteOperations.open_conn_and_login(IWI.MRBTS_IP,IWI.MRBTS_USERNAME,IWI.MRBTS_PASSWORD)
            # pingtest = self.remoteOperations.execute_command("ping 1.1.1.1 -c 4")
            pingtest = self.remoteOperations.execute_command("ping " + IWI.southboundIpAddress + " -c 4")
            package_loss = pingtest[-2].split(',')[-2].strip().split(' ')[0]
            # print package_loss
            self.remoteOperations.close_conn()
            if package_loss == "100%":
                logging.critical("MRBTS cannot communicate with BTSMED southbound, please check the connection")
                # exit()
            else:
                logging.critical("MRBTS can communicate with BTSMED southbound, continue")

    def check_ads_deploy_mrbts(self):
        if IWI.Integrate_MRBTS:
            logging.critical("Checking ADS deployment for " + IWI.NE_VERSION)
            self.remoteOperations.open_conn_and_login(IWI.NETACT_WAS_IP,IWI.OMC_USERNAME,IWI.OMC_PASSWORD)
            result = self.remoteOperations.execute_command("ls /d/oss/global/var/adaptations/o2ml | grep " + IWI.NE_VERSION +"$")
            self.remoteOperations.close_conn()
            if len(result) == 0:
                logging.critical("The adaptation for " + IWI.NE_VERSION + " is not deployed. Please deploy the adaptation first")
                exit()
            else:
                logging.critical("The adaptation for " + IWI.NE_VERSION + " is deployed. Continue integration.")

    def autoIntegMRBTS(self):
        if IWI.Integrate_MRBTS:
            logging.critical("Integrate MRBTS Start")
            self.AIM = AutoIntegration_MRBTS()
            self.AIM.integrate_MRBTS(IWI.NETACT_WAS_IP,IWI.NETACT_LBWAS,IWI.OMC_USERNAME,IWI.OMC_PASSWORD,IWI.MRBTS_DN,IWI.NE_HOST_NAME,IWI.EM_HOST_NAME,IWI.MR_NAME,IWI.NE_VERSION,IWI.HTTP_PORT,IWI.HTTPS_PORT,IWI.IP_VERSION,IWI.TLS_MODEL,IWI.credentials,IWI.cm_upload_flag)
            logging.critical("Integrate MRBTS Done")
        else:
            logging.critical("Integrate MRBTS -- Skipped")

    def workflow_process_mrbts(self):
        self.check_connectivity()
        self.check_ads_deploy_mrbts()
        self.autoConfigureDNS()
        self.autoInstallCert()
        self.autoIntegMRBTS()


if __name__ == '__main__':
    SW = Start_Workflow_MRBTS()
    # SW.check_connectivity()
    # SW.check_ads_deploy_mrbts()
    SW.workflow_process_mrbts()
    # SW.check_BTSMED_configue_file()
    # SW.autoconfigBTSMED()