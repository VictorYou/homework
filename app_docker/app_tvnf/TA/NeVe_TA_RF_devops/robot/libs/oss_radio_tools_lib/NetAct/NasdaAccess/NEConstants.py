'''
Copyright (c) Nokia Siemens Networks 2012
'''


class NEConstants(object):
    '''
    This class contains definitions for NASDA meta data
    that are frequently used as default parameters 
    for python method calls in different parts 
    in our TA libraries.
    
    Instead of hard-coding these default values into your
    python library declare the parameter here as an constant
    and refer to it from your library.
    Having definitions only in one place makes 
    possible future modifications of default values much easier.
    
    '''
  
    # NASDA ADAPTATION IDs
    NASDA_ID_PREFIX = 'com.nsn.netact.nasda'
    NASDA_AGENTS_ADAPTATION_ID = NASDA_ID_PREFIX + '.connectivity'
    NASDA_AGENT_INTERFACES_ID = NASDA_ID_PREFIX + '.interfaces'
    NASDA_COMMON_ADAPTATION_ID = NASDA_ID_PREFIX + '.common'
    
    NASDA_ID_SEPARATOR = ':'
    
    NASDA_WSDL_HTTP_URL = "http://INSERTHOSTHERE/netact/oss/nasda/ws-api/NasdaWSPersistencyServiceSOAP?wsdl"
    
    ADAPTATION_METAVERSION_BASE = 'base'
    ADAPTATION_METAVERSION = '1.0'
    
    MR_COMMON_CLASS_NAME = "MR"
    MRC_COMMON_CLASS_NAME = "MRC"
        
    MR_NASDA_CLASS_ID = NASDA_COMMON_ADAPTATION_ID + NASDA_ID_SEPARATOR + MR_COMMON_CLASS_NAME
    MRC_NASDA_CLASS_ID = NASDA_COMMON_ADAPTATION_ID + NASDA_ID_SEPARATOR + MRC_COMMON_CLASS_NAME
    
    # Nasda supported relation types
    NASDA_RELATION_AGENT = "AGENT"
    NASDA_RELATION_AGENT_REVERSED = "AGENT_REVERSED"
    NASDA_RELATION_MR = "MR"
    NASDA_RELATION_MR_REVERSED = "MR_REVERSED"   
    
    PLMN_CLASS_NAME = "PLMN"
    # AGENT CLASS NAMES
    AGENT_CLASS_NAME_AXC = "AXC"
    AGENT_CLASS_NAME_OMS = "OMS"
    AGENT_CLASS_NAME_RNC = "RNC"
    AGENT_CLASS_NAME_WBTS = "WBTS"
    AGENT_CLASS_NAME_IADA = "IADA"
    AGENT_CLASS_NAME_MRBTS = "MRBTS"
    AGENT_CLASS_NAME_RNC = "RNC"
    AGENT_CLASS_NAME_N3MU = "N3MU"
    AGENT_CLASS_NAME_OMGW = "OMGW"
    
    #The whole id of the (agent) class with the NASDA adaptation id (format: <Nasda adaptation ID>:<class name>) 
    PLMN_NASDA_CLASS_ID = NASDA_AGENTS_ADAPTATION_ID + NASDA_ID_SEPARATOR + PLMN_CLASS_NAME
    OMS_NASDA_AGENT_CLASS_ID = NASDA_AGENTS_ADAPTATION_ID + NASDA_ID_SEPARATOR + AGENT_CLASS_NAME_OMS
    AXC_NASDA_AGENT_CLASS_ID = NASDA_AGENTS_ADAPTATION_ID + NASDA_ID_SEPARATOR + AGENT_CLASS_NAME_AXC
    RNC_NASDA_AGENT_CLASS_ID = NASDA_AGENTS_ADAPTATION_ID + NASDA_ID_SEPARATOR + AGENT_CLASS_NAME_RNC
    IADA_NASDA_AGENT_CLASS_ID = NASDA_AGENTS_ADAPTATION_ID + NASDA_ID_SEPARATOR + AGENT_CLASS_NAME_IADA
    MRBTS_NASDA_AGENT_CLASS_ID = NASDA_AGENTS_ADAPTATION_ID + NASDA_ID_SEPARATOR + AGENT_CLASS_NAME_MRBTS
    WBTS_NASDA_AGENT_CLASS_ID = NASDA_AGENTS_ADAPTATION_ID + NASDA_ID_SEPARATOR + AGENT_CLASS_NAME_WBTS
    N3MU_NASDA_AGENT_CLASS_ID = NASDA_AGENTS_ADAPTATION_ID + NASDA_ID_SEPARATOR + AGENT_CLASS_NAME_N3MU
    
    # left for backwards compatibility (possibly in use)
    OMS_ADAPTATION_ID = OMS_NASDA_AGENT_CLASS_ID
    
    # Agent objects common attribute names
    AGENT_ATTR_INTEGRATION_FLAG = "directIntegration"
    AGENT_ATTR_VERSION = "version"
    
    # Agent interface class names and their attributes
    '''
    <b:managedObjectDef b:metaClass="com.nsn.netact.nasda.interfaces:NWI3" b:metaVersion="1.0">
                  <b:pDef name="id" type="Integer"/>
                  <b:pDef name="nwi3Mode" type="Integer"/>
                  <b:pDef name="nwi3SystemId" type="String"/>
                  <b:pDef name="version" type="String"/>
    </b:managedObjectDef>
    '''
    
    AGENT_IF_CLASS_NAME_NWI3 = "NWI3"
    AGENT_IF_CLASS_NAME_HTTP = "HTTP"
    # NWI3 interface class attributes
    NWI3_SYSTEM_ID = 'nwi3SystemId'
    # NWI3_HOST_NAME = 'hostName'
    NWI3_MODE = "nwi3Mode"
     
    '''
     <b:managedObjectDef b:metaClass="com.nsn.netact.nasda.interfaces:HTTP" b:metaVersion="1.0">
                  <b:pDef name="hostName" type="String"/>
                  <b:pDef name="id" type="Integer"/>
                  <b:pDef name="port" type="Integer"/>
                  <b:pDef name="securityMode" type="Integer"/>
                  <b:pDef name="version" type="String"/>    
    '''
    HTTP_HOST_NAME = 'hostName'
    HTTP_PORT = 'port'
    HTTP_SECURITY_MODE = 'securityMode'
    
    GEN_ATTR_ID = 'id'
    GEN_ATTR_VERSION = 'version'
    
    AGENT_IF_CLASS_NAME_MML = "MML"
    AGENT_IF_CLASS_NAME_SSH = "SSH"
    AGENT_IF_CLASS_NAME_EM = "EM"    
    AGENT_IF_CLASS_NAME_HTTP = "HTTP"       
            
    # Agent interface class id with the NASDA adaptation id (format: <Nasda adaptation ID>:<class name>) 
    NWI3_AGENT_IF_NASDA_CLASS_ID = NASDA_AGENT_INTERFACES_ID + NASDA_ID_SEPARATOR + AGENT_IF_CLASS_NAME_NWI3
    EM_AGENT_IF_NASDA_CLASS_ID = NASDA_AGENT_INTERFACES_ID + NASDA_ID_SEPARATOR + AGENT_IF_CLASS_NAME_EM
    MML_AGENT_IF_NASDA_CLASS_ID = NASDA_AGENT_INTERFACES_ID + NASDA_ID_SEPARATOR + AGENT_IF_CLASS_NAME_MML
    SSH_AGENT_IF_NASDA_CLASS_ID = NASDA_AGENT_INTERFACES_ID + NASDA_ID_SEPARATOR + AGENT_IF_CLASS_NAME_SSH  
    HTTP_AGENT_IF_NASDA_CLASS_ID = NASDA_AGENT_INTERFACES_ID + NASDA_ID_SEPARATOR + AGENT_IF_CLASS_NAME_HTTP  
    HTTP_AGENT_IF_NASDA_CLASS_ID = NASDA_AGENT_INTERFACES_ID + NASDA_ID_SEPARATOR + AGENT_IF_CLASS_NAME_HTTP    

    # The fixed instance id of the agent interface classes
    AGENT_IF_FIXED_ID = "1"
    
    # left for backwards compatibility (possibly in use)
    NWI3_AGENT_INTERFACE_ADAPTATION_ID = NWI3_AGENT_IF_NASDA_CLASS_ID    
    
    def __init__(self):
        '''
        Constructor
        '''

        
