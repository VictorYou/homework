#[Log Level]
# loglevel = "CRITICAL"
loglevel = "INFO"

#[NEType]
NE_Type='BTSMED'

#[NetAct Infor]
Integrate_BTSMED = True
#Integrate_BTSMED = False
NETACT_WAS_IP = "10.92.71.76"
NETACT_LBWAS = "clab523lbwas.netact.nsn-rdnet.net"
OMC_USERNAME = "omc"
OMC_PASSWORD = "omc"
BTSMED_DN = "PLMN-PLMN/BTSMED-1"
NE_HOST_NAME = "btsmed-1.nokia.com"
# Confiure_DNS = True
Confiure_DNS = False
MR_NAME = "MRC-MRC/MR-BTSMED"
NE_VERSION = "BTSMED18"
#TLS_MODEL = "tls"#
TLS_MODEL = "notls"
HTTP_PORT = "8080"
HTTPS_PORT = "8443"
IP_VERSION = "ipv4"
credentials = {"SOAM Web Service Access" : {"username": "wsuser", "password": "wspassword", "group": "sysop"}}
#credentials = {"SOAM Web Service Access" : {"username": "wsuser", "password": "wspassword", "group": "sysop"},"SSH Access" : {"username": "Nemuadmin", "password": "nemuuser", "group": "sysop"}}
cm_upload_flag = False

#[Install certificate to NetAct]
Install_NetAct_Certificate = False
#Install_NetAct_Certificate = True
NetAct_ROOT_PWD = "arthur"

#Install_NetAct_Certificate = False

#[CMP Server Infor]
caSubjectName = "C=CN, O=NOKIA, CN=CA_NETACT_TEST_TLS"
cmpPreSharedKey = "6kA8-4nD7-bzVB-Qq8s"
cmpRefNum = "9558"
serverHost = "10.91.83.136"
serverPort = "8081"
ca_id_of_CA = "10"

#[BTSMED Infor]
# Reconfigure_BTSMED = True
init_id = 1
Reconfigure_BTSMED = False
dnsIPAddress = '10.91.81.26'
northboundGateway = '10.91.80.1'
northboundIpAddress = '10.91.82.200'
southboundGateway = '10.92.16.1'
southboundIpAddress = '10.92.19.149'
#tlsModeNorthbound = 'Forced'
tlsModeNorthbound = 'Off'
BTSMED_ROOT_USER = 'toor4nsn'
BTSMED_ROOT_PWD = 'oZPS0POrRieRtu'

#[Upgrade BTSMED]
# Upgrade_BTSMED = True
Upgrade_BTSMED = False
New_BTSMED_rpm_link = 'http://hztdci01.china.nsn-net.net/job/IMP_SBTS17A_P7_RPM_PACKAGE/175//artifact/IMP/installation/target/rpm/nokia-imp/RPMS/noarch/nokia-imp-17a.2.20180228.6790b5-1.noarch.rpm'
#New_BTSMED_rpm_link = ''