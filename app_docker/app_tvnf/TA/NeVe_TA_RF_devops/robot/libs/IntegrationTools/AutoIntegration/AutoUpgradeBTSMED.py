from oss_radio_tools_lib.Remote.RemoteOperations import RemoteOperations
from oss_radio_tools_lib.Remote.LocalFileOperations import LocalFileOperations
import logging
import paramiko
import os
import time
import urllib2

class Upgrade_BTSMED(object):
    def __init__(self, remote_operations=None):
        if remote_operations is None:
            self.remote_operations = RemoteOperations()
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename='AutoUpgradeBTSMED.log',
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

    def check_hosts_file(self):
        logging.info("Check hosts file start.")
        result = self.remote_operations.execute_command('cat /etc/hosts | grep hztdci01.china.nsn-net.net')
        if len(result) == 0:
            logging.info("Configure hosts file start.")
            self.remote_operations.execute_command('echo 10.159.215.254 hztdci01.china.nsn-net.net >> /etc/hosts')
            logging.info("Configure hosts file cone.")
        logging.info("Check hosts file done.")

    def check_installed_sw(self):
        logging.info("Check installed software start.")
        result = self.remote_operations.execute_command('rpm -qa | grep nokia-imp')
        if len(result) == 0:
            logging.info("No software is installed")
            return None
        if len(result) > 1:
            logging.info("Multiple BTSMED softwares were installed")
            exit("Multiple BTSMED softwares were installed")
        if len(result) == 1:
            logging.info("Current BTSMED verison: " + result[0].strip())
            return result[0].strip()
        logging.info("Check installed software done.")


    def get_new_rpm(self,download_link):
        rpm_package_name = download_link.split('/')[-1].strip('.rpm')
        # print rpm_package_name
        return rpm_package_name

    def uninstall_current_rpm(self,installed_sw):
        logging.info("Uninstall current BTSMED rpm start")
        self.remote_operations.execute_command_ignore_error('rpm -e ' + installed_sw)
        logging.info("Uninstall current BTSMED rpm done")

    def install_new_rpm(self,download_link):
        logging.info("Install new BTSMED rpm start")
        self.remote_operations.execute_command_ignore_error('rpm -i ' + download_link.split('/')[-1])
        logging.info("Install new BTSMED rpm done")

    def download_new_rpm(self,download_link):
        logging.info("Download new BTSMED rpm start")
        remoteFileSize = self.getRemoteFileSize(download_link)
        # print remoteFileSize
        self.remote_operations.execute_command_with_immediately_output('wget ' + download_link + ' &')
        n = 0
        for n in range(120):
            time.sleep(10)
            n += 1
            # print n
            fsize = self.remote_operations.execute_command('ls -l ' + download_link.split('/')[-1] + '| awk \'{ print $5 }\'')[0]
            # print "downloading file size = " + str(fsize)
            # check_ps = self.remote_operations.execute_command('ps aux | grep '+ download_link + ' | grep -v grep')
            if int(fsize) < remoteFileSize:
                logging.info("Downloading Progress: " + str(round(float(float(fsize)/float(remoteFileSize)*100),2)) + "%")
                continue
            else:
                break
        if n == 120:
            logging.info("Download new BTSMED rpm timeout")
            return False
        else:
            logging.info("Download new BTSMED rpm done")
            return True

    def upgradeBTSMED(self,BTSMED_IP,BTSMED_DOWNLOAD_LINK,BTSMED_ROOT_USER="toor4nsn",BTSMED_ROOT_PWD="oZPS0POrRieRtu"):
        self.remote_operations.open_conn_and_login(BTSMED_IP,BTSMED_ROOT_USER,BTSMED_ROOT_PWD)
        self.check_hosts_file()
        rpm_name = BTSMED_DOWNLOAD_LINK.split('/')[-1]
        installed_sw = self.check_installed_sw()
        if installed_sw == self.get_new_rpm(BTSMED_DOWNLOAD_LINK):
            logging.info("The same version is installed, no need to upgrade")
        else:
            if self.remote_operations.check_file_exist("/home/toor4nsn/" + rpm_name):
                logging.info("BTSMED Installation RPM already exists")
            else:
                logging.info("Download BTSMED installation package " + rpm_name + " Start")
                if self.download_new_rpm(BTSMED_DOWNLOAD_LINK):
                    logging.info("Download BTSMED installation package " + rpm_name + " Done")
                else:
                    logging.info("Download BTSMED installation package " + rpm_name + " Failed")
                    exit("Fail to download the installation package.")
            if installed_sw != None:
                self.uninstall_current_rpm(installed_sw)
            self.install_new_rpm(BTSMED_DOWNLOAD_LINK)
            if self.check_installed_sw() == self.get_new_rpm(BTSMED_DOWNLOAD_LINK):
                logging.info("Upgrade BTSMED installation package:" + rpm_name + " Done")

    def getRemoteFileSize(self, download_link, proxy=None):
        opener = urllib2.build_opener()
        if proxy:
            if download_link.lower().startswith('https://'):
                opener.add_handler(urllib2.ProxyHandler({'https' : proxy}))
            else:
                opener.add_handler(urllib2.ProxyHandler({'http' : proxy}))
        try:
            request = urllib2.Request(download_link)
            request.get_method = lambda: 'HEAD'
            response = opener.open(request)
            response.read()
        except Exception, e:
            return 0
        else:
            fileSize = dict(response.headers).get('content-length', 0)
            logging.info("Remote File size = " + str(fileSize))
            return int(fileSize)

if __name__ == '__main__':
    ub = Upgrade_BTSMED()
    ub.upgradeBTSMED('10.91.83.128','http://hztdci01.china.nsn-net.net/job/IMP_xL18_RPM_PACKAGE/179//artifact/IMP/installation/target/rpm/nokia-imp/RPMS/noarch/nokia-imp-18.1.20180301133746.f4be9c-1.noarch.rpm')

