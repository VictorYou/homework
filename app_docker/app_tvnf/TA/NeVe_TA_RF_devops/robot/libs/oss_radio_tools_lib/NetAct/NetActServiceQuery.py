import re
import logging

from oss_radio_tools_lib.Remote.RemoteOperations import RemoteOperations


class NetActServiceQuery(object):
    COMMAND_SMANAGER_QUERY_SERVICE = "/opt/cpf/sbin/smanager.pl status service "

    def __init__(self, remote_operations=None, root_password="arthur"):
        if remote_operations is None:
            raise AssertionError("Must provide remote operations object")
        else:
            self.remoteOperations = remote_operations
            self.root_password = root_password

    def get_node(self, smanger_result):
        logging.info("Get_node start.")
        node = smanger_result.split(':')[1]
        logging.info("Get_node Done.")
        return node

    def get_host_from_the_domain_name(self, domain_name):
        logging.info("Get host from " + domain_name + " start.")
        host_information = self.remoteOperations.execute_command_with_root("host " + domain_name, self.root_password)
        regular_ip = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
        ips = []
        for ip in regular_ip.findall(host_information[0]):
            ips.append(ip)
            logging.info("ip>>>" + ip)
        logging.info("Get host from " + domain_name + " done.")
        return str(ips[0])

    def get_server_domainname(self, Service_name):
        Service_name = Service_name.lower()
        logging.info("Get " + Service_name + " server hostname start.")
        smanager_result = self.remoteOperations.execute_command_with_root(
            self.COMMAND_SMANAGER_QUERY_SERVICE + Service_name, self.root_password)
        dict_domain = {}
        for n in smanager_result:
            n = str(n.strip().lower())
            if n.startswith(Service_name):
                dict_domain[n.split(':')[0]] = n.split(':')[1]
        logging.info("Get " + Service_name + " server hostname done.")
        return dict_domain

    def get_server_ip(self, Service_name):
        dict_domain = self.get_server_domainname(Service_name)
        logging.info("Get IP for service hostname start.")
        dict_ip = {}
        for service, domainname in dict_domain.items():
            dict_ip[service] = self.get_host_from_the_domain_name(domainname)
        logging.info("Get IP for service hostname done.")
        return dict_ip


# if __name__ == "__main__":
#     opera = RemoteOperations()
#     conn = opera.open_conn_and_login('10.91.116.80','omc','1421--User')
#     netact=NetActServiceQuery(opera)
#     print netact.get_server_domainname("was")
#     print netact.get_server_ip('was')
