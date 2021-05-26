#[Log Level]
# loglevel = "CRITICAL"
loglevel = "INFO"

#[NEType]
NE_Type='MRBTS'

#[NetAct Infor]
Integrate_MRBTS = True
#Integrate_BTSMED = False
NETACT_WAS_IP = "10.91.81.29"
NETACT_LBWAS = "clab523lbwas.netact.nsn-rdnet.net"
OMC_USERNAME = "omc"
OMC_PASSWORD = "omc"
MRBTS_DN = "PLMN-PLMN/MRBTS-1771"
NE_HOST_NAME = "mrbts-1771.nokia.com"
EM_HOST_NAME = "10.91.227.159"
# Confiure_DNS = True
Confiure_DNS = False
MR_NAME = "MRC-MRC/MR-MRBTS1771"
NE_VERSION = "SBTS17A"
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

#[BTSMED Infor]
northboundIpAddress = '10.91.82.200'
southboundIpAddress = '10.91.152.15'



#[CMP Server Infor]
caSubjectName = "C=CN, O=NOKIA, CN=CA_NETACT_TEST_TLS"
cmpPreSharedKey = "6kA8-4nD7-bzVB-Qq8s"
cmpRefNum = "9558"
serverHost = "10.91.83.136"
serverPort = "8081"
ca_id_of_CA = "10"

#[MRBTS Infor]
MRBTS_IP = '10.91.227.159'
MRBTS_USERNAME = 'toor4nsn'
MRBTS_PASSWORD = 'oZPS0POrRieRtu'
