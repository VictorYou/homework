from NasdaOperations import *   
from Utils.Logger import LOGGER
__version__ = '0.0.1'

"""NasdaMethods is a wrapper class for custom NASDA operations.

Author: AC Tre + lahteen1
"""

class NasdaMethods(NasdaOperations):
    
    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'
    ROBOT_LIBRARY_VERSION = __version__        
   
    def createPlmn(self, moId = "", metaClass = NASDA_ADAP_ID + NEC.NASDA_ID_SEPARATOR + "PLMN", metaVersion = METAVERSION):
        '''
        Create PLMN
        Example values:
        moId = "PLMN-NWI3"
        metaClass = "com.nsn.netact.nasda.connectivity:PLMN"
        metaVersion = "1.0"
        ''' 
        return self.createMO(moId, metaClass, metaVersion)    
    def createOmsAgent(self, moId = '',metaClass = NASDA_ADAP_ID + NEC.NASDA_ID_SEPARATOR + "OMS", metaVersion = METAVERSION):
        '''
        Create OMS Agent
        Example values:
        moId = "PLMN-NWI3/OMS-1"
        metaClass = "com.nsn.netact.nasda.connectivity:OMS"
        metaVersion = "1.0"
        ''' 
        return self.createMO(moId, metaClass, metaVersion)
    def createAxcAgent(self, moId = '',metaClass = NASDA_ADAP_ID + NEC.NASDA_ID_SEPARATOR + "AXC", metaVersion = METAVERSION):
        '''
        Create AXC Agent
        Example values:
        moId = "PLMN-NWI3/AXC-1"
        metaClass = "com.nsn.netact.nasda.connectivity:AXC"
        metaVersion = "1.0"
        ''' 
        return self.createMO(moId, metaClass, metaVersion)        
    def createNwi3Interface(self, moId = "", metaClass = NASDA_INT_ID + NEC.NASDA_ID_SEPARATOR + "NWI3", metaVersion = METAVERSION, nwi3SystemId = None, hostName = ""):
        '''
        Create NWI3 Interface
        Example values:
        moId = "PLMN-NWI3/OMS-1/NWI3-1"
        metaClass = "com.nsn.netact.nasda.interfaces:NWI3"
        metaVersion = "1.0"
        nwi3SystemId = "NE-OMS-1"
        hostName = "1.2.3.4"
        ''' 
        if nwi3SystemId is not None:
            return self.createMO(moId, metaClass, metaVersion, {NEC.NWI3_HOST_NAME: hostName, NEC.NWI3_SYSTEM_ID: nwi3SystemId})
        else:
            return self.createMO(moId, metaClass, metaVersion, {NEC.NWI3_HOST_NAME: hostName})   
    def createHttpInterface(self, moId = '', metaClass = NASDA_INT_ID + NEC.NASDA_ID_SEPARATOR + "HTTP", metaVersion = METAVERSION, port = None, hostName = '1.2.3.4'):
        '''
        Create HTTP Interface
        Example values:
        moId = "PLMN-NWI3/OMS-1/HTTP-1"
        metaClass = "com.nsn.netact.nasda.interfaces:HTTP"
        metaVersion = "1.0"
        port = "12345"
        hostName = "1.2.3.4"
        ''' 
        return self.createMO(moId, metaClass, metaVersion, {NEC.NWI3_HOST_NAME: hostName, 'port': port})
    def getNWI3Interface(self, moId = ''):
        return self.getMO(moId)
 
if __name__ == '__main__':
    NASDAHOST = "casarini.netact.noklab.net"    
    nasda = NasdaMethods(NASDAHOST)    
       
    #print "Nasda operations: %s" % dir(nasda)
    #nasda.printMetadata()
    #exit(0)
    
    #print nasda._get_nasda_meta_class_and_version('PLMN-NATE/OMS-3513')
    
    #list[list[]...]: fqdn, {parameters}, operation=""
    oList=[["PLMN-NAT2"],["PLMN-NAT2/OMS-1666"],["PLMN-NAT2/RNC-1666"],
           ["PLMN-NAT2/OMS-1666/NWI3-666",{'hostName': '11.2.33.4', 'nwi3SystemId': 'NE-OMS-1666'}]]    
    #print "Create PLMN-NAT2 and some objects"    
    #nasda.create_update_delete_objects(oList)

    #nasda.delete_objects(oList)
    
    #rsp = nasda.getMO('PLMN-NATE/OMS-313')
    
    attr=nasda.get_mo_attributes('PLMN-NATE/OMS-313/NWI3-1')
    LOGGER.info(str(attr))
    

    #rsp = nasda.createPlmn("PLMN-NAT3", NASDA_ADAP_ID)
    #rsp = nasda.createOmsAgent("PLMN-NAT3/OMS-316", NASDA_ADAP_ID)
    rsp = nasda.createNwi3Interface('PLMN-NAT3/OMS-313/NWI3-1', nwi3SystemId='NE-OMS-313', hostName='10.3.1.3') 
    #rsp = nasda.createHttpInterface('PLMN-NAT3/OMS-313/HTTP-1', port='8080', hostName='10.1.2.3')
    #rsp = nasda.createAxcAgent("PLMN-NAT3/AXC-313", NASDA_ADAP_ID)

    #print str(rsp)
    #nasda.printResponse(rsp)
    #nasda.verifyResponse(rsp)
    exit(0)
