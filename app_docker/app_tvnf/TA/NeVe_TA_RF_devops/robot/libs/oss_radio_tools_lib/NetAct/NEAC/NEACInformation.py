__author__ = 'x5luo'


class NEACInformation(object):
    NEAC_Service_Information = {
        "SOAM Web Service Access": {
            "username": "userName",
            "password": "password"
        },
        "Web Service Access": {
            "username": "userName",
            "password": "password"
        },
        "EM Access": {
            "username": "emAccessUserName ",
            "password": "emAccessPassword"
        },
        "NWI3 Access": {
            "username": "nwi3UserName",
            "password": "nwi3Password"
        },
        "Default Access": {
            "username": "userName",
            "password": "password"
        },
        "NEUM Admin Access": {
            'username': 'neumAdminUserName',
            'password': 'neumAdminPassword'
        },
        'FTAM Access': {
            'username': 'ftamUserName',
            'password': 'ftamPassword'
        },
        'FTP Access': {
            'username': 'ftpUserName',
            'password': 'ftpPassword'
        },
        'Generic NE FTP Access': {
            'username': 'username',
            'password': 'password'
        },
        'HTTP Access': {
            'username': 'httpUserName',
            'password': 'httpPassword'
        },
        'HTTPS Access': {
            'username': 'httpsUserName',
            'password': 'httpsPassword'
        },
        'MML Access': {
            'username': 'mmlUserName',
            'password': 'mmlPassword'
        },
        'NEUM Admin Access': {
            'username': 'username',
            'password': 'password'
        },
        'NWI3 Access': {
            'username': 'nwi3UserName',
            'password': 'nwi3Password'
        },
        'Q1 Access': {
            'username': 'q1UserName',
            'password': 'q1Password'
        },
        'Q3 Access': {
            'username': 'q3UserName',
            'password': 'q3Password'
        },
        'Remote MML Access': {
            'username': 'remotemmlUserName',
            'password': 'remotemmlPassword'
        },
        'SCLI Access': {
            'username': 'scliUserName',
            'password': 'scliPassword'
        },
        'SFTP Access': {
            'username': 'sftpUserName',
            'password': 'sftpPassword'
        },

        'SNMP Read Access': {
            'username': 'SNMP_GET_COMMUNITY_NAME'
        },
        'SNMP Write Access': {
            'username': 'SNMP_SET_COMMUNITY_NAME'
        },
        'SNMP v1 v2 Access': {
            'profiles': {
                'SNMP Read Access': {
                    'username': 'SNMP_GET_COMMUNITY_NAME'
                },
                'SNMP Write Access': {
                    'username': 'SNMP_SET_COMMUNITY_NAME'
                }
            }
        },
        'SNMP v3 Access': {
            'profiles': {
                'Authentication - No Privacy': {
                    'username': 'snmpUserName',
                    'snmpContextName': 'snmpContextName',
                    'snmpAuthProtocol': 'snmpAuthProtocol',
                    'snmpAuthPassphrase': 'snmpAuthPassphrase',
                },
                'No Authentication - No Privacy': {
                    'username': 'snmpUserName',
                    'snmpContextName': 'snmpContextName',
                },
                'Authentication - Privacy': {
                    'username': 'snmpUserName',
                    'snmpContextName': 'snmpContextName',
                    'snmpPrivacyProtocol': 'snmpPrivacyProtocol',
                    'snmpPrivacyPassphrase': 'snmpPrivacyPassphrase',
                    'snmpAuthProtocol': 'snmpAuthProtocol',
                    'snmpAuthPassphrase': 'snmpAuthPassphrase',
                },
                'Non-Context': {
                    'username': 'snmpUserName',
                    'snmpPrivacyProtocol': 'snmpPrivacyProtocol',
                    'snmpPrivacyPassphrase': 'snmpPrivacyPassphrase',
                    'snmpAuthProtocol': 'snmpAuthProtocol',
                    'snmpAuthPassphrase': 'snmpAuthPassphrase',
                },
                'Default': {
                    'username': 'snmpUserName',
                    'snmpContextName': 'snmpContextName',
                    'snmpPrivacyProtocol': 'snmpPrivacyProtocol',
                    'snmpPrivacyPassphrase': 'snmpPrivacyPassphrase',
                    'snmpAuthProtocol': 'snmpAuthProtocol',
                    'snmpAuthPassphrase': 'snmpAuthPassphrase',
                },
            }
        },
        'SS7 Access': {
            'username': 'ss7UserName',
            'password': 'ss7Password'
        },
        'SSH Access': {
            'username': 'sshUserName',
            'password': 'sshPassword'
        },
        'Telnet Access': {
            'username': 'telnetUserName',
            'password': 'telnetPassword'
        },
        'Web Service Access': {
            'username': 'userName',
            'password': 'password'
        },
        'Privileged User Access': {
            'username': 'userName',
            'password': 'password'
        },
        'PnP Access': {
            'username': 'userName',
            'password': 'password'
        }
    }

    def __init__(self):
        pass

    def get_service_information(self, service_name):
        for service, value in self.NEAC_Service_Information.items():
            if service == service_name:
                return value
        raise AssertionError("The service name is not support.")
