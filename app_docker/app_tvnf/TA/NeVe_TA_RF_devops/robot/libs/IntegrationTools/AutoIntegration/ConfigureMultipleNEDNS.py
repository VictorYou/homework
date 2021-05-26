# __author__ = 'x5luo'
import logging
import time
from oss_radio_tools_lib.Remote import RemoteOperations
from oss_radio_tools_lib.NetAct import NetActServiceQuery


class ConfigureNEDNS(object):
    NETACT_DEFAUT_ROOT_USERNAME = "root"
    DNS_CONFIGURE_FILE_PATH = "/var/named/chroot/var/named/"
    DNS_NAMED_CONF_FILE_FULL_PATH = "/var/named/chroot/etc/named.conf"
    COMMAND_SMANAGER_QUERY_SERVICE = "smanager.pl status service "

    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='ConfigureMultipleNEDNS.log',
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
        self.remoteOperations = RemoteOperations.RemoteOperations()
        self.netactServiceQuery = NetActServiceQuery.NetActServiceQuery(self.remoteOperations)
        self.username = None
        self.password = None
        self.root_password = None

    # def check_network_element_in_db_domain_file(self, domain_name, NE_host):
    #     file_name = self.get_db_domain_file_name_from_domain_name(domain_name)
    #     ne_name = self.get_ne_name_from_domain_name(domain_name)
    #     logging.info("Check NetWorks Element " + domain_name + " to " + file_name + " start.")
    #     result = self.remoteOperations.execute_command_with_root(
    #         " cat " + self.DNS_CONFIGURE_FILE_PATH + file_name + " |grep '" + ne_name + " * A * " + NE_host + "' | wc -l",
    #         self.root_password)
    #     exist = False
    #     if int(result[0]) > int(0):
    #         logging.info("The NE " + domain_name + " exists in " + file_name + ".")
    #         exist = True
    #     logging.info("Check NetWorks Element " + domain_name + " to " + file_name + " done.")
    #     return exist

    def get_db_domain_file_name_from_domain_name(self, domain_name):
        logging.info("Get db file name from %s start", domain_name)
        names = domain_name.split('.')
        file_name = "db"
        for i in range(1, len(names) - 2):
            file_name += "." + names[i]
        if names[len(names) - 1] != "":
            file_name += "." + names[len(names) - 2]
        logging.info("Get db file name from %s done", domain_name)
        return file_name

    def get_db_host_file_name_from_host(self, NE_host):
        logging.info("Get the addr_arpa file for " + NE_host + " start.")
        splited_host = NE_host.split('.')
        addr_arpa_name = "db." + splited_host[0] + "." + splited_host[1] + "." + splited_host[2]
        logging.info("Get name: " + addr_arpa_name)
        logging.info("Get the addr_arpa file for " + NE_host + " done.")
        return addr_arpa_name

    def get_ne_name_from_domain_name(self, domain_name):
        logging.info("Get NE Name from domain name start.")
        ne_name = domain_name.split('.')[0]
        logging.info("Get NE Name from domain name done.")
        return ne_name

    def delete_ne_dns_configure_in_db_domain_file(self, domain_name):
        logging.info("Delete %s dns configure in db domain name file start.", domain_name)
        file_name = self.get_db_domain_file_name_from_domain_name(domain_name)
        ne_name = self.get_ne_name_from_domain_name(domain_name)
        self.remoteOperations.execute_command_with_root(
            "sed -i '/" + ne_name + "/d' " + self.DNS_CONFIGURE_FILE_PATH + file_name, self.root_password)
        logging.info("Delete %s dns configure in db domain name file done.", domain_name)

    def delete_ne_dns_configure_in_db_host_file(self, host_name, domain_name):
        logging.info("Delete %s dns configure in db host file start.")
        file_name = self.get_db_host_file_name_from_host(host_name)
        self.remoteOperations.execute_command_with_root(
            "sed -i '/" + domain_name + "/d' " + self.DNS_CONFIGURE_FILE_PATH + file_name, self.root_password)
        logging.info("Delete %s dns configure in db host file done.")

    def check_and_delete_exist_dns_configure(self, NE_host):
        logging.info("Check and delete exist dns configure start.")
        result = self.remoteOperations.execute_command_with_root("nslookup " + NE_host + " | grep name",
                                                                 self.root_password, error_raise=False)
        if len(result) == 1 and result[0] == '':
            logging.info("No exist DNS configure information")
        else:
            exist_domain_name = result[0][result[0].find("=") + 1:].strip()
            self.delete_ne_dns_configure_in_db_domain_file(exist_domain_name)
            self.delete_ne_dns_configure_in_db_host_file(NE_host, exist_domain_name)
        logging.info("Check and delete exist dns configure done.")

    def add_network_element_in_db_domain_file(self, domain_name, NE_host):
        file_name = self.get_db_domain_file_name_from_domain_name(domain_name)
        ne_name = self.get_ne_name_from_domain_name(domain_name)
        logging.info("Add NetWorks Element " + domain_name + " to " + file_name + " start.")
        self.remoteOperations.execute_command_with_root(
            "echo -e '" + ne_name + " A " + NE_host + "' >>" + self.DNS_CONFIGURE_FILE_PATH + file_name,
            self.root_password)
        logging.info("Add NetWorks Element " + domain_name + " to " + file_name + " done.")

    def check_and_delete_network_element_in_db_domain_file(self, domain_name, NE_host):
        file_name = self.get_db_domain_file_name_from_domain_name(domain_name)
        # print file_name
        ne_name = self.get_ne_name_from_domain_name(domain_name)
        # print ne_name
        logging.info("Check NetWorks Element " + domain_name + " in " + file_name + " start.")
        check_ne_name = self.remoteOperations.execute_command_with_root(
            # "cat " + self.DNS_CONFIGURE_FILE_PATH + file_name + ' | grep ' + NE_host + ' | grep '+ ne_name + ' | wc -l',
            "cat " + self.DNS_CONFIGURE_FILE_PATH + file_name + ' | grep '+ ne_name + ' | wc -l',
            self.root_password)
        # print check_ne_name
        # print len(check_ne_name)
        if int(check_ne_name[0]) > 0 :
            logging.info("Check NetWorks Element " + domain_name + " in " + file_name + " done. The domain name already exists.")
            logging.info("Delete existing domain name")
            self.remoteOperations.execute_command_with_root("sed -i /" + ne_name + "/d " + self.DNS_CONFIGURE_FILE_PATH + file_name,self.root_password)
            # return True
        else:
            logging.info("Check NetWorks Element " + domain_name + " in " + file_name + " done. The domian name does not exist.")
            # return False

    def create_db_domain_file(self, file_name, domain_name, dns_service):
        logging.info("Create " + file_name + " start.")
        split_domain_names = domain_name.split('.')
        ne_parameter = split_domain_names[1]
        for i in range(2, len(split_domain_names)):
            ne_parameter += "." + split_domain_names[i]
        ne_parameter += "."
        content = "$ORIGIN " + ne_parameter + "\n" + \
                  "$TTL 3600\n" + \
                  ne_parameter + " IN SOA " + dns_service['dns-master'] + ".netact.nsn-rdnet.net. root." + \
                  dns_service['dns-master'] + ".netact.nsn-rdnet.net. (\n" + \
                  "      2008040700      ; Serial\n" + \
                  "      28800           ; Refresh\n" + \
                  "      1200            ; Retry\n" + \
                  "      604800          ; Expire\n" + \
                  "      3600 )          ; Minimum TTL\n" + \
                  "      NS      " + dns_service['dns-master'] + ".netact.nsn-rdnet.net.\n" + \
                  "      NS      " + dns_service['dns-slave'] + ".netact.nsn-rdnet.net.\n"
        self.remoteOperations.execute_command_with_root(
            "echo -e '" + content + "' >> " + self.DNS_CONFIGURE_FILE_PATH + file_name, self.root_password)
        self.remoteOperations.execute_command_with_root("chown named:named " + self.DNS_CONFIGURE_FILE_PATH + file_name,
                                                        self.root_password)
        self.remoteOperations.execute_command_with_root("chmod 640 " + self.DNS_CONFIGURE_FILE_PATH + file_name,
                                                        self.root_password)
        self.check_and_add_db_file_in_name_conf(ne_parameter,
                                                self.get_db_domain_file_name_from_domain_name(domain_name))
        logging.info("Create " + file_name + " done.")

    def check_db_domain_file_exist(self, filename):
        result = self.remoteOperations.execute_command_with_root("ls " + self.DNS_CONFIGURE_FILE_PATH + filename,
                                                                 self.root_password, error_raise=False)
        if result[0].strip() == self.DNS_CONFIGURE_FILE_PATH + filename:
            return True
        return False

    def check_and_create_db_domain_file(self, file_name, domain_name, dns_services):
        logging.info("Check and create " + file_name + " start.")
        if self.check_db_domain_file_exist(file_name):
            logging.info("The " + file_name + " exists.")
            return "FileExists"
        else:
            self.create_db_domain_file(file_name, domain_name, dns_services)
            logging.info("The " + file_name + " is created.")
            return "FileCreate"

    def configure_network_element_in_db_domain_file(self, domain_name, ne_host, dns_services):
        file_name = self.get_db_domain_file_name_from_domain_name(domain_name)
        logging.info("Configure NetWorks Element " + domain_name + " to " + file_name + " start.")
        file_check = self.check_and_create_db_domain_file(file_name, domain_name, dns_services)
        if file_check == "FileExists":
            self.check_and_delete_network_element_in_db_domain_file(domain_name, ne_host)
            self.add_network_element_in_db_domain_file(domain_name, ne_host)
        elif file_check == "FileCreate":
            self.add_network_element_in_db_domain_file(domain_name, ne_host)
        logging.info("Configure NetWorks Element " + domain_name + " to " + file_name + " done.")

    def create_db_host_file(self, db_host_file, ne_name, ne_host, dns_service):
        logging.info("Create " + db_host_file + " start.")
        split_host = ne_host.split('.')
        ne_parameter = split_host[2] + '.' + split_host[1] + '.' + split_host[0]
        content = "$ORIGIN " + ne_parameter + ".in-addr.arpa.\n" + \
                  "$TTL 3600\n" + \
                  ne_parameter + ".in-addr.arpa. IN SOA " + dns_service['dns-master'] + ".netact.nsn-rdnet.net. root." + \
                  dns_service['dns-master'] + ".netact.nsn-rdnet.net. (\n" + \
                  "      2008040700      ; Serial\n" + \
                  "      28800           ; Refresh\n" + \
                  "      1200            ; Retry\n" + \
                  "      604800          ; Expire\n" + \
                  "      3600 )          ; Minimum TTL\n" + \
                  "      NS      " + dns_service['dns-master'] + ".netact.nsn-rdnet.net.\n" + \
                  "      NS      " + dns_service['dns-slave'] + ".netact.nsn-rdnet.net.\n" + \
                  split_host[3] + "     PTR     " + ne_name + "."
        self.remoteOperations.execute_command_with_root(
            "echo -e '" + content + "' >> " + self.DNS_CONFIGURE_FILE_PATH + db_host_file, self.root_password)
        self.remoteOperations.execute_command_with_root(
            "chown named:named " + self.DNS_CONFIGURE_FILE_PATH + db_host_file, self.root_password)
        self.remoteOperations.execute_command_with_root("chmod 640 " + self.DNS_CONFIGURE_FILE_PATH + db_host_file,
                                                        self.root_password)
        self.check_and_add_db_file_in_name_conf(ne_parameter + ".in-addr.arpa.", db_host_file)
        logging.info("Create " + db_host_file + " done.")

    def configure_network_element_in_db_host_file(self, domain_name, NE_host, dns_services):
        file_name = self.get_db_host_file_name_from_host(NE_host)
        logging.info("Configure NetWorks Element " + domain_name + " to " + file_name + " start.")
        if self.check_db_domain_file_exist(file_name):
            self.configure_ne_information_in_exist_db_host_file(file_name, domain_name, NE_host)
        else:
            self.create_db_host_file(file_name, domain_name, NE_host, dns_services)
        logging.info("Configure NetWorks Element " + domain_name + " to " + file_name + " done.")

    def check_ne_information_exist_in_db_host_file(self, db_host_file, domain_name, ne_host):
        logging.info("Check NE information in " + db_host_file + " start.")
        split_host = ne_host.split('.')
        result = self.remoteOperations.execute_command_with_root(
            " cat " + self.DNS_CONFIGURE_FILE_PATH + db_host_file + " |grep '" + split_host[
                3] + " * PTR * " + domain_name + ".' | wc -l", self.root_password)
        exist = False
        if int(result[0]) > 0:
            logging.info("The " + domain_name + " exists in " + db_host_file)
            exist = True
        logging.info("Check NE information in " + db_host_file + " done.")
        return exist

    def add_ne_information_in_exist_db_host_file(self, db_host_file, domain_name, ne_host):
        logging.info("Add NE information in " + db_host_file + " start.")
        split_host = ne_host.split('.')
        self.remoteOperations.execute_command_with_root(
            "echo -e '" + split_host[3] + "   PTR    " + domain_name + ".' >>" +
            self.DNS_CONFIGURE_FILE_PATH + db_host_file, self.root_password)
        logging.info("Add NE information in " + db_host_file + " done.")

    def check_ne_information_exist_in_db_host_file(self, db_host_file, domain_name, ne_host):
        ne_name = self.get_ne_name_from_domain_name(domain_name)
        check_dn = self.remoteOperations.execute_command_with_root(
            "cat " + self.DNS_CONFIGURE_FILE_PATH + db_host_file + " | grep \"" + ne_name + "\\.\" | wc -l", self.root_password)
        if int(check_dn[0]) > 0:
            self.remoteOperations.execute_command_with_root(
                "sed -i /\"" + ne_name + "\\.\"/d " + self.DNS_CONFIGURE_FILE_PATH + db_host_file, self.root_password)

    def configure_ne_information_in_exist_db_host_file(self, db_host_file, domain_name, ne_host):
        logging.info("Configure NE information in " + db_host_file + " start.")
        self.check_ne_information_exist_in_db_host_file(db_host_file, domain_name, ne_host)
        self.add_ne_information_in_exist_db_host_file(db_host_file, domain_name, ne_host)
        logging.info("Configure NE information in " + db_host_file + " done.")

    def check_and_add_db_file_in_name_conf(self, title, file_name):
        logging.info("Check NE information in name.conf start.")
        logging.info("Title: " + title + " File name: " + file_name)
        addr_arpa_name = "'zone \"" + title + "\"'"
        result = self.remoteOperations.execute_command_with_root(
            "cat " + self.DNS_NAMED_CONF_FILE_FULL_PATH + " |grep " + addr_arpa_name + " |wc -l", self.root_password)
        if int(result[0]) > int(0):
            logging.info("The " + addr_arpa_name + " exists in name.conf")
        else:
            self.add_db_host_file_in_name_conf(title, file_name)
        logging.info("Check NE information in name.conf done.")

    def delete_exist_db_host_file_in_name_conf(self, title):
        logging.info("Delete exist NE information in named.conf start.")
        addr_arpa_name = "zone \"" + title + "\""
        self.remoteOperations.execute_command_with_root(
            "sed  -i '/^" + addr_arpa_name + "/,+3'd " + self.DNS_NAMED_CONF_FILE_FULL_PATH, self.root_password)
        logging.info("Delete exist NE information in named.conf done.")

    def add_db_host_file_in_name_conf(self, title, file_name):
        logging.info("Add db information in name.conf start.")
        content = "zone \"" + title + "\" {\n" + "      type master;\n" + "      file \"" + file_name + "\";\n" + "};\n"
        logging.info("Content: " + content)
        self.remoteOperations.execute_command_with_root(
            "echo -e '" + content + "' >>" + self.DNS_NAMED_CONF_FILE_FULL_PATH, self.root_password)
        logging.info("Add db information in name.conf done.")

    def restart_dns_service(self):
        logging.info("Restart dns service start.")
        result = self.remoteOperations.execute_command_with_root(
            " service named restart;echo $?", self.root_password)
        logging.info("Restart result: ")
        logging.info(result)
        index = -1
        if result[-1] == '':
            index = -2
        if int(result[index]) != 0:
            logging.info("Restart dns service failed.")
        logging.info("Restart dns service done.")

    def verify_dns_configuration(self, domain_name_dict):
        logging.info("Verify NE DNS configuration start.")
        time.sleep(5)
        for domain_name , ne_host in domain_name_dict.items():
            verify = True
            logging.info("Checking "+ domain_name + " and " + ne_host + " start.")
            if len(self.remoteOperations.execute_command_with_root("nslookup " + domain_name + " |grep " + ne_host,
                                                                   self.root_password)) == int(0):
                logging.error("Check the nslookup " + domain_name + " Failed.")
                verify = False
            if verify and len(
                    self.remoteOperations.execute_command_with_root("nslookup " + ne_host + " |grep " + domain_name,
                                                                    self.root_password)) == int(0):
                logging.error("Check the nslookup " + ne_host + " Failed.")
                verify = False
            if not verify:
                # raise AssertionError("Verify dns configuration failed.")
                return False
            logging.info("Verify NE DNS configuration done.")
        return True

    def configure_network_element_dns(self, domain_name_dict, dns_server_host, dns_services):
        logging.info("Configure DNS in " + dns_server_host + " start.")
        self.remoteOperations.open_conn_and_login(dns_server_host, self.username, self.password)
        # self.check_and_delete_exist_dns_configure(ne_host)
        for domain_name,ne_host in domain_name_dict.items():
            self.configure_network_element_in_db_domain_file(domain_name, ne_host, dns_services)
            self.configure_network_element_in_db_host_file(domain_name, ne_host, dns_services)
        self.restart_dns_service()
        result = self.verify_dns_configuration(domain_name_dict)
        self.remoteOperations.close_conn()
        logging.info("Configure DNS in " + dns_server_host + " done.")
        if result:
            logging.info("Configure DNS in " + dns_server_host + " Successfully!")
            # logging.critical("Configuring DNS in NetAct Successfully!")
        else:
            logging.info("Configure DNS in " + dns_server_host + " Failed")
            # logging.critical("Configuring DNS in NetAct Failed!")
            exit()

    def set_credential(self, username, password, root_password):
        self.username = username
        self.password = password
        self.root_password = root_password

    def configure_network_elements_dns(self, domain_name_dict, NetAct_host, username, password,
                                       root_password="arthur"):
        # logging.critical("Configuring DNS in NetAct Starts")
        self.set_credential(username, password, root_password)
        self.remoteOperations.open_conn_and_login(NetAct_host, username, password)
        dns_master_host = self.netactServiceQuery.get_server_ip("DNS-Master")
        dns_service_domain_name = self.netactServiceQuery.get_server_domainname("DNS")
        # print dns_master_host,dns_service_domain_name
        self.remoteOperations.close_conn()
        self.configure_network_element_dns(domain_name_dict, dns_master_host['dns-master'],
                                           dns_service_domain_name)


# remote_operations = RemoteOperations.RemoteOperations()
# remote_operations.open_conn_and_login('10.91.116.80', 'omc', '1421--User')
# remote_operations.execute_command_with_root("ls /home", "arthur")

if __name__ == "__main__":
    configureNEDNS = ConfigureNEDNS()
    # configureNEDNS.configure_network_elements_dns("sbs15.netact-radiact.cn", "10.58.251.225", "10.91.116.80",
    #                                               "omc", "1421--User", "arthur")
    # configureNEDNS.configure_network_elements_dns("btsmed-1.srbts.net", "10.91.43.173", "10.91.116.80",
    #                                                "omc", "omc", "arthur")
    #configureNEDNS.configure_network_elements_dns({"btsmed-1.netact.com":"10.91.85.17","mrbts-1771.netact.com":"10.91.85.17","mrbts-1779.netact.com":"10.91.85.17","mrbts-15.netact.com":"10.91.85.17"}, "10.91.85.2",
     #                                              "omc", "omc", "arthur")
    configureNEDNS.configure_network_elements_dns({"mrbts-1774.noksbell.com":"10.91.82.200","btsmed-1.noksbell.com":"10.91.82.200"}, "10.91.81.29",
                                                   "omc", "omc", "arthur")
    #configureNEDNS.configure_network_elements_dns({"mrbts-1779.netact.com":"10.91.83.128"}, "10.91.81.14","omc", "omc", "arthur")
    # NEName = raw_input("Please input the domain_name:")
    # NEHost = raw_input("Please input the NE IP:")ssh
    # LabHost = raw_input("Please input the NetAct node IP:")
    # username = raw_input("Please input the username of NetAct:")
    # password = raw_input("Please input the password of NetAct:")
    # root_password = raw_input("Please input the root password for NetAct:")
    # configureNEDNS.configure_network_elements_dns(NEName, NEHost, LabHost, username, password, root_password)
    # raw_input("Please enter any key to exit.")
