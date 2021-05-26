import logging
import time
import sys
from oss_radio_tools_lib.Remote.RemoteOperations import RemoteOperations
from oss_radio_tools_lib.NetAct.NetActServiceQuery import NetActServiceQuery

class TriggerAlarmUpload():
    def __init__(self):
        self.dmgrNodeIp = ""
        self.remoteoperations = RemoteOperations()
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='VerifyPMdata.log',
                            filemode='w')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def connectSpecificNode(self, netactnodeip, login_name, login_password):
        self.remoteoperations.open_conn_and_login(netactnodeip, login_name, login_password)
        netactServiceQuery = NetActServiceQuery(self.remoteoperations)
        serviceName = 'dmgr'
        nodeInfo = netactServiceQuery.get_server_ip(serviceName)
        if serviceName in nodeInfo.keys()[0]:
            self.dmgrNodeIp = nodeInfo[nodeInfo.keys()[0]]
        logging.info("========================")
        logging.info(nodeInfo)
        logging.info(self.dmgrNodeIp)
        logging.info("========================")
        self.remoteoperations.close_conn()
        self.remoteoperations.open_conn_and_login(self.dmgrNodeIp, login_name, login_password)

    def connectdmgrNode(self, omc_user, omc_password):
        self.remoteoperations.open_conn_and_login(self.dmgrNodeIp, omc_user, omc_password)

    def checkCertStatus(self):
        cmd = '/opt/oss/NSN-sm_hardening/bin/sshAccess4Users.sh --certStatus'
        output = self.remoteoperations.execute_command(cmd)
        return output

    def writeintoTmpfile(self, content, file):
        with open(file, "wb") as temp_file:
            for element in content:
                temp_file.write(element)

    def getomccert(self, file):
        omc_cert = "omc"
        is_omc_cert_exists = False
        with open(file, "r") as temp_file:
            for line in temp_file:
                if omc_cert in line:
                    output = line
                    is_omc_cert_exists = True
                else:
                    pass
        logging.info(output)
        return is_omc_cert_exists

    def executeaupbyfmcli(self, dn):
        cmd = '/opt/oss/NSN-fm_inst_monitoringdesktop/bin/fmCLI.sh -operation alarmupload -dn '+ dn
        logging.info(cmd)
        output = self.remoteoperations.execute_command(cmd)
        return output

    def getjobid(self, file):
        prefix = "jobid:"
        with open(file, "r") as temp_file:
            for line in temp_file:
                if prefix in line:
                    jobinfo = line.split(':')
        logging.info(jobinfo)
        return jobinfo[1].replace('\n', '')

    def getaupstatus(self, jobid):
        cmd = 'sh fmCLI.sh -operation status -jobid ' + jobid
        pattern_success = "SUCCESS"
        pattern_fail = "FAILURE"
        pattern_running = "RUNNING"
        aupstatus = ""
        logging.info(cmd)
        output = self.remoteoperations.execute_command(cmd)
        logging.info(output[0])
        if pattern_success in output[0]:
            aupstatus = True
        elif pattern_fail in output[0]:
            aupstatus = False
        else:
            aupstatus = "RUNNING"
        return aupstatus

    def creatcert2omc(self):
        cmd = '/opt/oss/NSN-sm_hardening/bin/sshAccess4Users.sh --modify --user omc --configCert 1D'
        output = self.remoteoperations.execute_command(cmd)
        logging.info(cmd)
        logging.info(output)

if __name__=='__main__':
    root_user = "root"
    root_password = "arthur"
    omc_user = "omc"
    omc_password = "omc"
    dmgrNodeIp = "10.32.214.232"
    dn = "PLMN-PLMN/MRBTS-801"
    taup = TriggerAlarmUpload()
    # login to dmgr node as root
    taup.connectSpecificNode(dmgrNodeIp, root_user, root_password)
    output = taup.checkCertStatus()
    taup.writeintoTmpfile(output, "aup_omc_certStatus.txt")
    is_omc_cert_exists = taup.getomccert("aup_omc_certStatus.txt")
    if is_omc_cert_exists == False:
        taup.creatcert2omc()
    #login to fmwas as omc
    taup.connectdmgrNode(omc_user, omc_password)
    output1 = taup.executeaupbyfmcli(dn)
    taup.writeintoTmpfile(output1, "aup_jobid.txt")
    jobid = taup.getjobid("aup_jobid.txt")
    print jobid
    time.sleep(90)
    aupstatus = taup.getaupstatus(jobid)
    print aupstatus


