import logging

from IntegrationTools.AutoIntegration.AutoIntegration_OMS import AutoIntegration_OMS
from IntegrationTools.AutoIntegration.AutoIntegration_BSC import AutoIntegration_BSC
from IntegrationTools.AutoIntegration.AutoIntegration_SBTS import AutoIntegration_SBTS


class AutoIntegration_robot(object):
    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='AutoIntegration_robot.log',
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        self.integration_gsm = AutoIntegration_BSC()
        self.integration_wcdma = AutoIntegration_OMS()
        self.integration_lte = AutoIntegration_OMS()
        self.integration_sbts = AutoIntegration_SBTS()

    def integration_GSMs(self, netact_host, omc_username, omc_password, ne_list):
        logging.info("Integrate GSMs start.")
        for ne in ne_list:
            if not self.integration_gsm.integrate_BSC(netact_host, omc_username, omc_password, ne['DN'], ne['NE_IP'],
                                                      ne['MR'], VERSION=ne['VERSION'],
                                                      AgentInterface=ne['AGENT_INTERFACE']):
                raise AssertionError("Integrate " + ne['DN'] + " failed.")
        logging.info("Integrate GSMs done.")

    def integration_WCDMAs(self, netact_host, omc_username, omc_password, ne_list):
        logging.info("Integrate WCDMA start.")
        for ne in ne_list:
            if not self.integration_wcdma.integrate_OMS(netact_host, omc_username, omc_password, ne['DN'], ne['NE_IP'],
                                                        ne['MR'], VERSION=ne['VERSION']):
                raise AssertionError("Integrate " + ne['DN'] + " failed")
        logging.info("Integrate WCDMA done.")

    def integration_LTEs(self, netact_host, omc_username, omc_password, ne_list):
        logging.info("Integrate LTE start.")
        for ne in ne_list:
            if not self.integration_lte.integrate_OMS(netact_host, omc_username, omc_password, ne['DN'], ne['NE_IP'],
                                                      ne['MR'], VERSION=ne['VERSION']):
                raise AssertionError("Integrate " + ne['DN'] + " failed")
        logging.info("Integrate LTE done.")

    def integration_SBTSs(self, netact_host, omc_username, omc_password, ne_list):
        logging.info("Integrate SBTS start.")
        for ne in ne_list:
            if not self.integration_sbts.integrate_SBTS(netact_host, omc_username, omc_password, ne['DN'], ne['NE_IP'],
                                                        ne['MR'], NE_VERSION=ne['VERSION'], TLS_MODEL=ne['TLS_MODEL']):
                raise AssertionError("Integrate " + ne['DN'] + " failed")
        logging.info("Integrate SBTS done.")

    def integration_nes(self, netact_host, omc_username, omc_password, type, ne_list):
        logging.info("Integrate " + type + " NEs start.")
        if type == "GSM":
            self.integration_GSMs(netact_host, omc_username, omc_password, ne_list)
        elif type == "WCDMA":
            self.integration_WCDMAs(netact_host, omc_username, omc_password, ne_list)
        elif type == "LTE":
            self.integration_LTEs(netact_host, omc_username, omc_password, ne_list)
        elif type == "SBTS":
            self.integration_SBTSs(netact_host, omc_username, omc_password, ne_list)
        else:
            raise AssertionError("Not support NE.")
        logging.info("Integrate " + type + " NEs done.")
