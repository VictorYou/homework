#  Copyright 2011 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from robot.libraries.BuiltIn import BuiltIn

ROOT_USER_VAR = '${SDV_ROOT_USER}'
ROOT_PASSWD_VAR = '${SDV_ROOT_PASSWORD}'
OMC_USER_VAR = '${SDV_DESKTOP_ADMIN_USER}'
OMC_PASSWD_VAR = '${SDV_DESKTOP_ADMIN_PASSWORD}'
DNS_DOMAIN = '${SDV_DNS_DOMAIN}'
APP_PRIMARY_HOST_VAR = '${SDV_WEBSPHERE_APPSERVER_PRIMARY}'
LB_WAS_HOSTS_VAR = '@{SDV_OSS_LB_WAS_HOSTS}'
COMMON_MEDIATION_HOSTS_VAR = '@{SDV_OSS_JBI_COMMONMEDIATION_HOSTS}'
WAS_DMGR_HOSTS_VAR = '@{SDV_OSS_WAS_DMGR_HOSTS}'
FM_PIPE_HOST_VAR = '@{SDV_OSS_JBI_FMPIPE_HOSTS}'
WS_AS_PRIMARY_FQDN_VAR = '${SDV_WEBSPHERE_APPSERVER_PRIMARY_FQDN}'
DB_HOSTNAME_FQDN_VAR = '${SDV_DB_HOSTNAME_FQDN}'
DB_OMC_PASSWD_VAR = '${SDV_DB_OMC_PASSWORD}'
DB_OMC_USER_VAR = '${SDV_DB_OMC_USER}'
ONEPM_NAS_USERNAME = '${SDV_ONEPM_NAS_USER}'
ONEPM_NAS_PASSWORD = '${SDV_ONEPM_NAS_PASSWORD}'
PM_MGR_HOSTS_VAR = '@{SDV_OSS_PM_MGR_HOSTS}'

# Mediations supported
NE3SWS_MEDIATION = "com.nsn.oss.mediation.south.ne3soapfm"
NE3SSNMP_MEDIATION = "com.nsn.oss.mediation.south.snmp" #Dropped in N8
NWI3_MEDIATION = "com.nsn.oss.nwi3.fm"
Q3_MEDIATION = "com.nsn.oss.q3.fm"
XOH_MEDIATION = "com.nsn.oss.mediation.south.xoh.fm"
NX2S_MEDIATION = "com.nsn.oss.mediation.south.nx2sfm"
NOKFING_MEDIATION = "com.nsn.oss.mediation.south.fing" #Dropped in N8
# MUS mediations
NE3SSNMP_PM_MEDIATION = 'com.nokia.oss.mediation.south.ne3spm'
SNMP_PM_MEDIATION = 'com.nokia.oss.mediation.south.snmppm'
NE3SSNMP_FM_MEDIATION = 'com.nokia.oss.mediation.south.snmpfm'
SNMP_FM_MEDIATION = 'com.nokia.oss.mediation.south.snmpfm'
# Adaptation specific mediations
JUNIPER_MEDIATION = 'com.nsn.oss.mediation.south.juniper.common'
INFOBLOX_MEDIATION = 'com.nsn.oss.mediation.south.paco.snmp'
FNS_MEDIATION = 'com.nsn.oss.mediation.south.fns.ftp'

MEDIATION_DEPLOYED_NODE = {
                           NE3SWS_MEDIATION: COMMON_MEDIATION_HOSTS_VAR,
                           NE3SSNMP_MEDIATION: WAS_DMGR_HOSTS_VAR, #Dropped in N8
                           NWI3_MEDIATION: '@{SDV_OSS_JBI_NWI3_HOSTS}',
                           Q3_MEDIATION: '@{SDV_OSS_JBI_Q3_HOSTS}',
                           XOH_MEDIATION: '@{SDV_OSS_JBI_NX2SXOH_HOSTS}',
                           NX2S_MEDIATION: '@{SDV_OSS_JBI_NX2SXOH_HOSTS}',
                           NOKFING_MEDIATION: COMMON_MEDIATION_HOSTS_VAR, #Dropped in N8
                           #SCLI
                           #MML
                           NE3SSNMP_PM_MEDIATION: '@{SDV_OSS_WAS_CLUSTER_NETACT_HOSTS}',
                           SNMP_PM_MEDIATION: '@{SDV_OSS_WAS_CLUSTER_NETACT_HOSTS}',
                           NE3SSNMP_FM_MEDIATION: '@{SDV_OSS_WAS_CLUSTER_NETACT_HOSTS}',
                           SNMP_FM_MEDIATION: '@{SDV_OSS_WAS_CLUSTER_NETACT_HOSTS}',
                           # Adaptation specific mediations
                           JUNIPER_MEDIATION: COMMON_MEDIATION_HOSTS_VAR,
                           INFOBLOX_MEDIATION: COMMON_MEDIATION_HOSTS_VAR,
                           FNS_MEDIATION: COMMON_MEDIATION_HOSTS_VAR

}

class VariablesHelper(object):
    """This library is used to manage variables from SDV file
    """

    def __init__(self):
        self.sdv_variables = BuiltIn().get_variables()
        self.sdv_desktop_admin_user = ''
        self.sdv_desktop_admin_password = ''
        self.sdv_root_user = ''
        self.sdv_root_password = ''
        self.sdv_dns_domain = ''
        self.sdv_ws_as_primary_fqdn = ''
        self.sdv_db_hostname_fqdn = ''
        self.sdv_db_omc_user = ''
        self.sdv_db_omc_password = ''

        self.pm_mgr_host_list = []

        self.nas_username = ''
        self.nas_password = ''

        self.sdv_websphere_appserver_primary_host = ''

        self.sdv_oss_lb_was_hosts = ''
        self.sdv_oss_jbi_commonmediation_hosts = ''
        self.sdv_oss_was_dmgr_hosts = ''
        self.was_dmgr_fqdn = ''

        self.med_fqdn_list = []
        self.med_node_list = []
        self.fm_pipe_node_list = []
        self.fm_fqdn_list = []

    def get_root_user(self):
        if not self.sdv_root_user:
            self.sdv_root_user = self._get_variable(ROOT_USER_VAR)
        return self.sdv_root_user

    def get_root_passwrd(self):
        if not self.sdv_root_password:
            self.sdv_root_password = self._get_variable(ROOT_PASSWD_VAR)
        return self.sdv_root_password

    def get_omc_user(self):
        if not self.sdv_desktop_admin_user:
            self.sdv_desktop_admin_user = self._get_variable(OMC_USER_VAR)
        return self.sdv_desktop_admin_user

    def get_omc_passwrd(self):
        if not self.sdv_desktop_admin_password:
            self.sdv_desktop_admin_password = self._get_variable(OMC_PASSWD_VAR)
        return self.sdv_desktop_admin_password

    def get_dns_domain(self):
        if not self.sdv_dns_domain:
            self.sdv_dns_domain = self._get_variable(DNS_DOMAIN)
        return self.sdv_dns_domain

    def get_ws_as_primary_fqdn(self):
        if not self.sdv_ws_as_primary_fqdn:
            self.sdv_ws_as_primary_fqdn = self._get_variable(WS_AS_PRIMARY_FQDN_VAR)
        return self.sdv_ws_as_primary_fqdn

    def get_mediation_node(self, mediation_fm=None):
        """Use to get mediation node according to the fm mediation id .
        @ mediation_fm: fm mediation id , such as com.nsn.oss.mediation.south.ne3soapfm.
        """
        if mediation_fm is None:
            mediation_hosts = self._get_variable(COMMON_MEDIATION_HOSTS_VAR)
        else:
            mediation_node_var = MEDIATION_DEPLOYED_NODE[mediation_fm]
            mediation_hosts = self._get_variable(mediation_node_var)
        return mediation_hosts[0]

    def get_mediation_nodes(self, mediation_fm=None):
        """Use to get mediation nodes according to the fm mediation id.
        @ mediation_fm: fm mediation id, such as com.nsn.oss.mediation.south.ne3soapfm.
        """
        if not self.med_node_list:
            if mediation_fm is None:
                self.med_node_list = self._get_variable(COMMON_MEDIATION_HOSTS_VAR)
            else:
                mediation_node_var = MEDIATION_DEPLOYED_NODE[mediation_fm]
                self.med_node_list = self._get_variable(mediation_node_var)
            return self.med_node_list

    def get_med_fqdn_list(self, mediation_fm=None):
        if not self.med_fqdn_list:
            self.med_fqdn_list = self._get_fqdn_list(self.get_mediation_nodes(mediation_fm))
        return self.med_fqdn_list

    def get_fm_pipe_nodes(self):
        if not self.fm_pipe_node_list:
            self.fm_pipe_node_list = self._get_variable(FM_PIPE_HOST_VAR)
        return self.fm_pipe_node_list

    def get_fm_fqdn_list(self):
        if not self.fm_fqdn_list:
            self.fm_fqdn_list = self._get_fqdn_list(self.get_fm_pipe_nodes())
        return self.fm_fqdn_list

    def _get_fqdn_list(self, node_list):
        fqdn_list = []
        for node in node_list:
            fqdn = '%s.%s' % (node, self.get_dns_domain())
            fqdn_list.append(fqdn)
        return fqdn_list

    def get_primary_server_node(self):
        """Use to get primary server node
        """
        if not self.sdv_websphere_appserver_primary_host:
            self.sdv_websphere_appserver_primary_host = self._get_variable(APP_PRIMARY_HOST_VAR)
        return self.sdv_websphere_appserver_primary_host

    def get_lb_was_node(self):
        """Use to get load balance node
        """
        if not self.sdv_oss_lb_was_hosts:
            self.sdv_oss_lb_was_hosts = self._get_variable(LB_WAS_HOSTS_VAR)
        return self.sdv_oss_lb_was_hosts[0]

    def get_was_dmgr_node(self):
        """Use to get was dmgr node
        """
        if not self.sdv_oss_was_dmgr_hosts:
            self.sdv_oss_was_dmgr_hosts = self._get_variable(WAS_DMGR_HOSTS_VAR)
        return self.sdv_oss_was_dmgr_hosts[0]

    def get_was_dmgr_fqdn(self):
        if not self.was_dmgr_fqdn:
            self.was_dmgr_fqdn = '%s.%s' % (self.get_was_dmgr_node(), self.get_dns_domain())
        return self.was_dmgr_fqdn

    def get_db_hostname_fqdn(self):
        """Use to get db hostname fqdn
        """
        if not self.sdv_db_hostname_fqdn:
            self.sdv_db_hostname_fqdn = self._get_variable(DB_HOSTNAME_FQDN_VAR)
        return self.sdv_db_hostname_fqdn

    def get_db_omc_user(self):
        if not self.sdv_db_omc_user:
            self.sdv_db_omc_user = self._get_variable(DB_OMC_USER_VAR)
        return self.sdv_db_omc_user

    def get_db_omc_passwrd(self):
        if not self.sdv_db_omc_password:
            self.sdv_db_omc_password = self._get_variable(DB_OMC_PASSWD_VAR)
        return self.sdv_db_omc_password

    def get_pm_mgr_hosts(self):
        if not self.pm_mgr_host_list:
            self.pm_mgr_host_list = self._get_variable(PM_MGR_HOSTS_VAR)
        return self.pm_mgr_host_list

    def get_nas_user(self):
        if not self.nas_username:
            self.nas_username = self._get_variable(ONEPM_NAS_USERNAME)
        return self.nas_username

    def get_nas_passwrd(self):
        if not self.nas_password:
            self.nas_password = self._get_variable(ONEPM_NAS_PASSWORD)
        return self.nas_password

    def judge_variable_exist_or_not(self, name):
        if name in self.sdv_variables.keys():
            return True
        else:
            return False

    def _get_variable(self, name):
        """
        NOTE: the self._sdv_variables is a robot defined object, its
         type is robot.running.namespace._VariableScopes, not dict type.
        """
        if not name:
            print "*WARN* Get SDV variables using empty name."
        if name in self.sdv_variables.keys():
            return self.sdv_variables[name]
        else:
            raise AssertionError("please check your variables file for definition of %s" % (str(name)))
