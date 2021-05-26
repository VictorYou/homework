import logging
import time
import sys
from oss_radio_tools_lib.Remote.RemoteOperations import RemoteOperations
from oss_radio_tools_lib.NetAct.NetActServiceQuery import NetActServiceQuery

class VerifyNewPMData():
    WORK_FILE_PATH1 = "PMrecord1"
    WORK_FILE_PATH2 = "PMrecord2"
    def __init__(self):
        self.anyNodeIp = ""
        self.omcName = ""
        self.omcPwd = ""
        self.dbschema = ""
        self.cmd = ""
        self.runtime = ""
        self.table = ""
        self.pmNodeIP = ""
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

    def connectPMNode(self, anyNodeIp, omcName, omcPwd):
        self.anyNodeIp = anyNodeIp
        self.omcName = omcName
        self.omcPwd = omcPwd
        self.remoteoperations.open_conn_and_login(self.anyNodeIp, self.omcName, self.omcPwd)
        netactServiceQuery = NetActServiceQuery(self.remoteoperations)
        serviceName = 'db_crons'
        self.pmNodeIP = netactServiceQuery.get_server_ip(serviceName)[serviceName]
        self.remoteoperations.close_conn()
        self.remoteoperations.open_conn_and_login(self.pmNodeIP, self.omcName, self.omcPwd)

    def runCmd(self, dbschema):
        self.cmd = 'etlcolDBInfo.pl -t ' + dbschema + '_PV%RAW'
        output = self.remoteoperations.execute_command(self.cmd)
        return output

    def writeTmpfile(self, content, file):
        with open(file, "wb") as temp_file:
            for element in content:
                temp_file.write(element)

    def getRuncmdTime(self, file):
        self.runtime = "Analysis executed:"
        with open(file, "r") as temp_file:
            for line in temp_file:
                if self.runtime in line:
                    output = line
                else:
                    pass
        logging.info(output)
        return output


    def getTableContent(self, file, dbschema):
        dict = {}
        self.table = dbschema + "_PV_"
        with open(file, "r") as temp_file:
            for line in temp_file:
                if self.table in line:
                    tableinfo = line.split()
                    #print(tableinfo)
                    dict[tableinfo[0]] = tableinfo[2]
                else:
                    pass
        print(dict)
        return dict

    def comparePMdata(self, firstPMdict, secondPMdict, dbschema):
        self.dbschema = dbschema
        if 0 == cmp(firstPMdict, secondPMdict):
            logging.info(" No pm data coming for " +self.dbschema)
            return False
        else:
            for key in firstPMdict.keys():
                if firstPMdict[key] != secondPMdict[key]:
                    logging.info(key + " has new pm data coming")
            return True

    def main(self):
        self.connectPMNode()
        output = self.runCmd()
        self.writeTmpfile(output, self.WORK_FILE_PATH1)
        time1 = self.getRuncmdTime(self.WORK_FILE_PATH1)
        dict1 = self.getTableContent(self.WORK_FILE_PATH1)
        print("=============================")
        time.sleep(30)
        output = self.runCmd()
        self.writeTmpfile(output, self.WORK_FILE_PATH2)
        time2 = self.getRuncmdTime(self.WORK_FILE_PATH2)
        dict2 = self.getTableContent(self.WORK_FILE_PATH2)
        print("First fetch time: " + time1)
        print("Second fetch time: " + time2)
        pm_data_coming = self.comparePMdata(dict1, dict2)


if __name__=='__main__':

#    anyNodeIp = sys.argv[1]
#    omcName = sys.argv[2]
#    omcPwd = sys.argv[3]
#    dbschema = sys.argv[4]
    anyNodeIp = "10.32.214.236"
    omcName = "omc"
    omcPwd = "omc"
    dbschema = "SMAPMA"
#    vnpd = VerifyNewPMData(anyNodeIp, omcName, omcPwd, dbschema)
#    sys.exit(vnpd.main())
    vnpd = VerifyNewPMData()
    vnpd.connectPMNode(anyNodeIp, omcName, omcPwd)
    output = vnpd.runCmd(dbschema)
    vnpd.writeTmpfile(output, "PMrecord1")
    time1 = vnpd.getRuncmdTime("PMrecord1")
    dict1 = vnpd.getTableContent("PMrecord1", dbschema)
    time.sleep(10)
    output = vnpd.runCmd(dbschema)
    vnpd.writeTmpfile(output, "PMrecord2")
    time2 = vnpd.getRuncmdTime("PMrecord2")
    dict2 = vnpd.getTableContent("PMrecord2", dbschema)
    pm_data_coming = vnpd.comparePMdata(dict1, dict2, dbschema)

