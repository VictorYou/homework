#!/usr/bin/python
#from NasdaAccess.NasdaInterface.NasdaWSPersistency_client import NasdaWSPersistency_client
from NasdaAccess.NasdaInterface import NasdaWSPersistency_client
from NEConstants import NEConstants as NEC
from ZSI.auth import AUTH
#from robot.variables import GLOBAL_VARIABLES
from robot.libraries.BuiltIn import BuiltIn
from Utils.Logger import LOGGER

__version__ = '0.4.5'

"""NasdaOperations is a core library for NASDA operations.

Python SOAP library ZSI is used: http://pywebsvcs.sourceforge.net/zsi.html

https://confluence.inside.nokiasiemensnetworks.com/display/CMOP/NASDA+WebService+Persistency

Author: AC Tre + lahteen1 + pesaarel
"""

model = 'http://www.nsn.com/schemas/public/oss/nasda/ws-api/persistency/model'

'''Constants from NEConstants:'''
METAVERSION = NEC.ADAPTATION_METAVERSION
NASDA_ADAP_ID = NEC.NASDA_AGENTS_ADAPTATION_ID
NASDA_INT_ID = NEC.NASDA_AGENT_INTERFACES_ID


class NasdaAccessor(NasdaWSPersistency_client.NasdaWSPersistencyPortBindingSOAP):
    def __init__(self, wsdlLocation, login, passwd):
        NasdaWSPersistency_client.NasdaWSPersistencyPortBindingSOAP.__init__(self, None)
        self.locator = NasdaWSPersistency_client.NasdaWSPersistencyServiceLocator()
        self.port = self.locator.getNasdaWSPersistencyPort(wsdlLocation)
        self.port.binding.SetAuth(AUTH.httpbasic, login, passwd)
        self.binding = self.port.binding


class NasdaOperations(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LIBRARY_VERSION = __version__

    NasdaMetadata = None

    '''
    ################
    INTERNAL METHODS
    '''

    def __init__(self, HOST=None, login="omc", passwd="omc"):
        self.CreatedObjects = []  # List of DNs, can be used in cleanup
        wsdlLocationURL = None
        if HOST is None:
            # Try to get variables from robot env
            try:
                asList = BuiltIn().get_variable_value('@{BACKEND1_OMC}')
                wsdlLocationURL = NEC.NASDA_WSDL_HTTP_URL.replace("INSERTHOSTHERE", asList[0])
            except Exception as e:
                LOGGER.debug(
                    "NasdaOperations:__init__: Host information not specified and could not get BACKEND1_OMC info from robot environment." \
                    " Exception: " + str(e))
                LOGGER.trace("\nNasdaOperations initialized without host information." + "\n")
        elif not '://' in HOST:
            wsdlLocationURL = NEC.NASDA_WSDL_HTTP_URL.replace("INSERTHOSTHERE", HOST)
        else:
            wsdlLocationURL = HOST
        if wsdlLocationURL != None:
            self.nasda = NasdaAccessor(wsdlLocationURL, login, passwd)
            LOGGER.trace("\n\nNasdaOperations initialized as " + str(
                self.nasda) + ".\n" + "wsdlLocationURL = " + wsdlLocationURL + "\n")

    def _parseMONameFromDN(self, DN):
        if '/' not in DN:
            if '-' in DN:
                MO = DN[:DN.find('-')]
            else:
                MO = DN
        else:
            MO = DN[DN.rfind('/') + 1:DN.find('-', DN.rfind('/'))]
        return MO

    def _createMOPathFromDN(self, DN):
        '''
        PLMN-PLMN/RNC-181/EM-1 -> /PLMN[instance()='PLMN'/RNC[instance()='181']/EM[instance()='1']
        '''
        dn = DN.split('/')
        MOP = ""
        for d in dn:
            MOP = MOP + '/' + d[:d.find('-')] + "[instance()='" + d[d.find('-') + 1:] + "']"
        return MOP

    def _getMetadata(self):
        '''
        Returns all NASDA (Netact System Data Access) metadata
        '''
        if self.NasdaMetadata is None:
            self.NasdaMetadata = self.nasda.getMetadata(NasdaWSPersistency_client.getMetadataRequest())
        return self.NasdaMetadata

    def _createMO(self, moId, metaClass, metaVersion=METAVERSION, params=None):
        '''
        Create MO
        Example values:
        moId = "PLMN-PLMN/OMS-1"
        metaClass = "com.nsn.netact.nasda.connectivity"
        metaVersion = "1.0"
        params = {'hostName': '1.2.3.4', 'nwi3SystemId': 'NE-OMS-1'}
        '''
        LOGGER.trace("NasdaOperations._createMO called with parameters " + str(self) + " " + str(moId) + " " + str(
            metaClass) + " " + str(metaVersion) + " " + str(params))
        request = NasdaWSPersistency_client.createManagedObjectsRequest()
        mo = request.new_managedObject()
        mo.set_attribute_moId(moId)

        if NEC.NASDA_ID_SEPARATOR not in metaClass:
            MO = self._parseMONameFromDN(moId)
            metaClass = metaClass + NEC.NASDA_ID_SEPARATOR + MO

        mo.set_attribute_metaVersion(metaVersion)
        mo.set_attribute_metaClass(metaClass)
        if params is not None:
            newparams = []
            for param in params:
                newparam = mo.new_p(params[param])
                newparam.set_attribute_name(param)
                newparams.append(newparam)
                mo.set_element_p(newparams)
        request.set_element_managedObject([mo])
        return self.nasda.createManagedObjects(request)

    def _createRelationship(self, sourceMoId, targetMoId, relationship):
        '''
        Create relationship between two objects
        Example values:
        @param sourceMoId: "PLMN-PLMN/RNC-1"
        @param targetMoId: "PLMN-PLMN/OMS-1"
        @param relationship: "AGENT"
        @return: soap request response object
        '''
        LOGGER.trace("NasdaOperations._createRelationship called with parameters " + str(self) + " " + str(
            sourceMoId) + " " + str(targetMoId) + " " + str(relationship))
        req = NasdaWSPersistency_client.createRelationshipsRequest()
        LOGGER.trace("createRelationshipsRequest dict: %s " % dir(req))
        rel = req.new_relationship()
        LOGGER.trace("relationship dict: %s " % dir(rel))
        source_mo = rel.new_sourceMOId(sourceMoId)
        rel.set_element_sourceMOId(source_mo)
        LOGGER.trace("source moid dict: %s" % dir(source_mo))
        LOGGER.trace("source moid: %s" % source_mo)
        target_mo = rel.new_targetMOId(targetMoId)
        LOGGER.trace("target moid: %s" % target_mo)
        rel.set_element_targetMOId(target_mo)
        rel.set_element_relationshipId(relationship)
        req.set_element_relationship([rel])
        return self.nasda.createRelationships(req)

    def _getMO(self, moId):
        '''
        Read and return MO data
        '''
        LOGGER.debug("NasdaOperations._getMO fetching MO data for " + str(moId) + "\n")
        req = NasdaWSPersistency_client.getManagedObjectsRequest()
        mo = req.new_moId(moId)
        req.set_element_moId([mo])
        return self.nasda.getManagedObjects(req)

    def _getRelatedMOs(self, moId, relationship="CHILD"):
        '''
        Get Related MOs

        @param moId: managed object id e.g. "PLMN-PLMN"
        @param relationship: relationship of returned objects. Values: "CHILD" (default) or "PARENT"
        @return: getRelatedMOLitesResponse object
        '''
        req = NasdaWSPersistency_client.getRelatedMOLitesRequest()
        mo = req.new_moId(moId)
        req.set_element_moId([mo])
        req.set_element_relationship(relationship)
        return self.nasda.getRelatedMOLites(req)

    def _updateMO(self, moId, metaClass, metaVersion=METAVERSION, params=None):
        '''
        Update MO
        Example values:
        moId = "PLMN-NWI3/OMS-1"
        metaClass = "com.nsn.netact.nasda.connectivity:OMS"
        params = {'hostName': '1.2.3.4', 'nwi3SystemId': 'NE-OMS-1'}
        '''
        LOGGER.trace("NasdaOperations._updateMO called with parameters " + str(self) + " " + str(moId) + " " + str(
            metaClass) + " " + str(metaVersion) + " " + str(params))
        req = NasdaWSPersistency_client.updateManagedObjectsRequest()
        mo = req.new_managedObject()

        if NEC.NASDA_ID_SEPARATOR not in metaClass:
            MO = self._parseMONameFromDN(moId)
            metaClass = metaClass + NEC.NASDA_ID_SEPARATOR + MO

        mo.set_attribute_metaClass(metaClass)
        mo.set_attribute_metaVersion(metaVersion)
        mo.set_attribute_moId(moId)
        if params is not None:
            newparams = []
            for param in params:
                newparam = mo.new_p(params[param])
                newparam.set_attribute_name(param)
                newparams.append(newparam)
                mo.set_element_p(newparams)
        req.set_element_managedObject([mo])
        return self.nasda.updateManagedObjects(req)

    def _compare_dn_depth(self, first, second):
        if first.count('/') > second.count('/'):
            return -1
        elif first.count('/') < second.count('/'):
            return 1
        else:
            return 0

    def _deleteMO(self, moId):
        '''
        Delete Managed Object
        @param moId: Managed Object Id e.g. "PLMN-PLMN/OMS-1"
        @return: deleteManagedObjectsResponse object
        '''
        LOGGER.trace("NasdaOperations._deleteMO called with parameters " + str(self) + " " + str(moId))
        LOGGER.debug("NasdaOperations._deleteMO deleting object " + str(moId))
        req = NasdaWSPersistency_client.deleteManagedObjectsRequest()
        # LOGGER.trace("deleteReq: %s" % dir(req))
        mo = req.new_moId(moId)
        #LOGGER.trace("moId: %s" % dir(mo))
        req.set_element_moId([mo])
        return self.nasda.deleteManagedObjects(req)

    def _deleteMOs(self, moIdList):
        '''
        Delete list of Managed Object
        @param moIdList: List of managed object ids e.g. ["PLMN-PLMN","PLMN-PLMN/OMS-1","PLMN-PLMN/OMS-1/NWI3-1"]
        @return: deleteManagedObjectsResponse object
        '''
        LOGGER.trace("NasdaOperations._deleteMOs called with parameters " + str(self) + " " + str(moIdList))
        moIdList.sort(self._compare_dn_depth)
        LOGGER.debug("Delete moId's in this order: %s" % moIdList)
        req = NasdaWSPersistency_client.deleteManagedObjectsRequest()
        LOGGER.trace("deleteReq:%s" % dir(req))
        req.set_element_moId(moIdList)
        return self.nasda.deleteManagedObjects(req)

    def _deleteRelationship(self, sourceMoId, targetMoId, relationship):
        '''
        Delete managed object relationship
        Example values:
        @param sourceMoId: "PLMN-PLMN/RNC-1"
        @param targetMoId: "PLMN-PLMN/OMS-1"
        @param relationship: "AGENT"
        '''
        LOGGER.trace("NasdaOperations._deleteRelationship called with parameters " + str(self) + " " + str(
            sourceMoId) + " " + str(targetMoId) + " " + str(relationship))
        req = NasdaWSPersistency_client.deleteRelationshipsRequest()
        LOGGER.trace("deleteRelationshipsRequest dict: %s " % dir(req))
        rel = req.new_relationship()
        LOGGER.trace("relationship dict: %s " % dir(rel))
        source_mo = rel.new_sourceMOId(sourceMoId)
        rel.set_element_sourceMOId(source_mo)
        LOGGER.trace("source moid dict: %s" % dir(source_mo))
        LOGGER.trace("source moid: %s" % source_mo)
        target_mo = rel.new_targetMOId(targetMoId)
        LOGGER.trace("target moid: %s" % target_mo)
        rel.set_element_targetMOId(target_mo)
        rel.set_element_relationshipId(relationship)
        req.set_element_relationship([rel])
        return self.nasda.deleteRelationships(req)

    def _printResponse(self, rsp):
        LOGGER.info("Response dict:%s" % rsp.__dict__)
        LOGGER.info("Response dir:%s" % dir(rsp))
        result = rsp.get_element_result()
        resDict = dir(result)
        LOGGER.info("result dir:%s" % resDict)
        if resDict.__contains__('BatchItemMOResult'):
            batch = result.get_element_batchItemMOResult()
            for item in batch:
                LOGGER.info("batch item:%s" % dir(item))
                # errors
                if item.get_element_errorCause() != None:
                    LOGGER.warn("Error: %s" % item.get_element_errorCause())
                    return
                mo = item.get_element_managedObject()
                LOGGER.info("mo dir:%s" % dir(mo))
                LOGGER.info("moId:%s" % mo.get_attribute_moId())
                LOGGER.info("metaClass:%s" % mo.get_attribute_metaClass())
                LOGGER.info("metaVersion:%s" % mo.get_attribute_metaVersion())
                ps = mo.get_element_p()
                if hasattr(ps, '__contains__'):
                    LOGGER.info("ps:%s" % dir(ps))
                    for p in ps:
                        LOGGER.info("Param:%s=%s" % (p._attrs['name'], p))
        if resDict.__contains__('BatchItemMOLiteResult'):
            batch = result.get_element_batchItemMOLiteResult()
            for item in batch:
                resdict = item.__dict__
                for item in resdict:
                    if resdict[item].find('\n') >= 0:
                        LOGGER.info(str(item) + "," + str(resdict[item][:resdict[item].find('\n')]))
                    else:
                        LOGGER.info(str(item) + "," + str(resdict[item]))
        if rsp.get_element_cause() != None:
            LOGGER.info(rsp.get_element_cause())

    def _verifyResponse(self, rsp, fail_on_error=False, no_warns=False):
        '''
        Analyses SOAP request response object for an error.
        @param rsp: soap request response object
        @param fail_on_error: When True, Raises an AssertionError if request failed. False is default value.
        @param no_warns: When True, changes *WARN* messages to *INFO* level, useful for negative cases, when errors are expected.
        @return: Returns 0 (zero) if request was successful otherwise request failed.
        @raise AssertionError: if fail_on_error==True or rsp is of unknown formatting
        '''
        LOGGER.trace("\nNasdaOperations._verifyResponse called with parameters " + str(self) + " " + str(rsp))
        # LOGGER.trace("response = " + str(dir(rsp)))

        rc = 0

        if no_warns == True:
            error_log_level = "*INFO* "
        else:
            error_log_level = "*WARN* "

        if dir(rsp).__contains__('get_element_result'):
            try:
                # Normal response
                result = rsp.get_element_result()
            except:
                try:
                    # if e.g. relationship is not created successfully
                    if dir(rsp).__contains__('get_element_cause'):
                        LOGGER.info(error_log_level + "NASDA Error occurred! : %s\n%s" \
                                    % (rsp.get_element_errorCode(), rsp.get_element_cause()[:200]))
                        LOGGER.debug("NASDA Complete errorCause:\n%s" % rsp.get_element_cause())
                        result = "REL"
                        rc = 1
                    else:
                        raise AssertionError(
                            "*ERROR* NASDA._verifyResponse: Could not parse NASDA response, unknown formatting.")
                except:
                    raise AssertionError(
                        "*ERROR* NASDA._verifyResponse: Could not parse NASDA response, unknown formatting.")
                    # If relationship creation is successful
        elif dir(rsp).__contains__('get_element_relationship'):
            result = rsp.get_element_relationship()
            LOGGER.debug("NASDA operation succeeded.\n")
        else:
            raise AssertionError("*ERROR* NASDA._verifyResponse: Could not parse NASDA response, unknown formatting.")

        resDict = dir(result)

        # MO creation
        if resDict.__contains__('BatchItemMOResult'):
            batch = result.get_element_batchItemMOResult()
            for item in batch:
                #LOGGER.trace("batch item:%s" % dir(item))
                # errors
                if item.get_element_errorCause() != None:
                    LOGGER.info(error_log_level + "NASDA Error occurred! : %s\n%s" \
                                % (item.get_element_errorCode(),
                                   item.get_element_errorCause()[:item.get_element_errorCause().find('\n')]))
                    LOGGER.debug("NASDA Complete errorCause:\n%s" % item.get_element_errorCause())
                    rc = 1
                else:
                    LOGGER.debug("NASDA operation succeeded.\n")
        # MO deletion
        elif resDict.__contains__('BatchItemMOLiteResult'):
            batch = result.get_element_batchItemMOLiteResult()
            for item in batch:
                #LOGGER.trace("batch item:%s" % dir(item))
                # errors
                if item.get_element_errorCause() != None:
                    # If errorCause row has a sentence beginning with 'Caused by', let's print that in WARN message
                    if 'Caused by: ' in str(item.get_element_errorCause()):
                        cause = str(item.get_element_errorCause())
                        cause = cause[cause.find('Caused by: '):]
                        cause = cause[:cause.find('\n')]
                        LOGGER.info(error_log_level + "NASDA Error occurred! : %s\n%s\n%s" \
                                    % (item.get_element_errorCode(),
                                       item.get_element_errorCause()[:item.get_element_errorCause().find('\n')], cause))
                    else:
                        LOGGER.info(error_log_level + "NASDA Error occurred! : %s\n%s" \
                                    % (item.get_element_errorCode(),
                                       item.get_element_errorCause()[:item.get_element_errorCause().find('\n')]))
                    LOGGER.debug("NASDA Complete errorCause:\n%s" % item.get_element_errorCause())
                    rc = 1
                else:
                    LOGGER.debug("NASDA operation succeeded.\n")
        # if relationship is not created successfully (e.g. SystemException)
        elif resDict.__contains__('BatchItemRelationshipResult'):
            batch = result.get_element_batchItemRelationshipResult()
            for item in batch:
                #LOGGER.trace("batch item:%s" % dir(item))
                # errors
                if item.get_element_errorCause() != None:
                    LOGGER.info(error_log_level + "NASDA Error occurred! : %s\n%s" \
                                % (item.get_element_errorCode(),
                                   item.get_element_errorCause()[:item.get_element_errorCause().find('\n')]))
                    LOGGER.debug("NASDA Complete errorCause:\n%s" % item.get_element_errorCause())
                    rc = 1
                else:
                    LOGGER.debug("NASDA operation succeeded.\n")
        elif result != "REL":
            LOGGER.debug(str(resDict))
            raise AssertionError("*ERROR* NASDA._verifyResponse: Could not parse NASDA response, unknown formatting.")

        if rc != 0 and fail_on_error != False:
            raise AssertionError("*ERROR* NASDA Error(s) occurred! For explanation, see WARN(s) above.")
        print
        return rc

    def _create_vb(self, ele_vbs, key, value):
        ele_vb = ele_vbs.new_variableBinding(value)
        ele_vb.set_attribute_name("key")
        return ele_vb

    def _query_molites(self, query, variableBindings={}):
        req = NasdaWSPersistency_client.queryMOLitesRequest()
        ele_q = req.new_query(query)
        req.set_element_query(ele_q)
        if (len(variableBindings) > 0):
            ele_vbs = req.new_variableBindings()
            ele_vbs.set_element_variableBinding(
                map(lambda x: self._create_vb(ele_vbs, x[0], x[1]), variableBindings.items()))
            req.set_element_variableBindings(ele_vbs)
        return self.nasda.queryMOLites(req)

    '''
    ########################
    PUBLIC METHODS AND UTILS
    '''

    def verify_agent_connectivity_attribute(self, connectivityList):
        errorList = []
        meta = self._getMetadata()
        result = meta.get_element_result()
        reldef = result.get_element_relationshipDefs().get_element_relationshipDef()
        for conn in connectivityList:
            LOGGER.debug("Check %s" % str(conn))
            errorMsg = ""
            for rel in reldef:
                srcMeta = rel.get_attribute_sourceMetaClass()
                targetMeta = rel.get_attribute_targetMetaClass()
                if len(conn) == 3:
                    if srcMeta and targetMeta \
                            and srcMeta[srcMeta.rfind(NEC.NASDA_ID_SEPARATOR) + 1:] == conn[0] \
                            and targetMeta[targetMeta.rfind(NEC.NASDA_ID_SEPARATOR) + 1:] == conn[1] \
                            and conn[2] in self.get_mo_attributenames_from_metadata(conn[1]):
                        errorMsg = ""
                        break
                    else:
                        errorMsg = "%s has no attribute %s" % (conn[1], conn[2])
                else:
                    errorMsg = "Connectivity info should be 3 length, %s" % str(conn)
            if errorMsg:
                LOGGER.warn("%s" % errorMsg)
                errorList.append(errorMsg)
        if len(errorList) > 0:
            raise AssertionError("Agent connectivity check failed.")


    def setNasdaHost(self, HOST=None, login="omc", passwd="omc"):
        wsdlLocationURL = None
        if HOST is None:
            raise AttributeError("HOST must be defined!")
        elif not '://' in HOST:
            wsdlLocationURL = NEC.NASDA_WSDL_HTTP_URL.replace("INSERTHOSTHERE", HOST)
        else:
            wsdlLocationURL = HOST
        if wsdlLocationURL != None:
            self.nasda = NasdaAccessor(wsdlLocationURL, login, passwd)
            LOGGER.debug("NasdaHost set as " + str(wsdlLocationURL))

    # ------------------new keywords for nasda only --------------------
    def _get_sorted_and_reverse_object_list(self, object_list):
        """This is used to sort the object_list or reversely sort object_list.
        """
        list1 = []
        sorted_object_list = []
        reverse_object_list = []
        for obj in object_list:
            obj_list = obj[0].split("/")
            obj_len = len(obj_list)
            list1.append((obj_len, obj))
        list2 = sorted(list1, key=lambda d: d[0], reverse=False)
        list3 = sorted(list1, key=lambda d: d[0], reverse=True)
        [sorted_object_list.append(i[1]) for i in list2]
        [reverse_object_list.append(i[1]) for i in list3]
        return (sorted_object_list, reverse_object_list)

    def create_objects(self, objectList, fail_on_first_error=True):
        LOGGER.trace("Create objects with parameter: %s" % str(objectList))
        self._create_root_objects(objectList)
        sortedObjectList, _ = self._get_sorted_and_reverse_object_list(objectList)
        for obj in sortedObjectList:
            moId, parameters = self._get_object_info(obj)
            metaClass, metaVersion = self.get_mo_metaclass_and_version(moId)
            response = self._createMO(moId, metaClass, metaVersion, parameters)
            rc = self._verifyResponse(response)
            if rc != 0:
                if fail_on_first_error:
                    raise AssertionError("NASDA Error occurred when create object: " + str(moId) +
                                         "! For explanation, see WARN above.")
                else:
                    LOGGER.warn("NASDA Error occurred when create object: " + str(moId) +
                                "! For explanation, see WARN above.")

    def update_objects(self, objectList):
        LOGGER.trace("Update objects with parameter: %s" % str(objectList))
        sortedObjectList, _ = self._get_sorted_and_reverse_object_list(objectList)
        for obj in sortedObjectList:
            moId, parameters = self._get_object_info(obj)
            metaClass, metaVersion = self.get_mo_metaclass_and_version(moId)
            response = self._updateMO(moId, metaClass, metaVersion, parameters)
            rc = self._verifyResponse(response)
            if rc != 0:
                raise AssertionError("NASDA Error occurred when update object: " + str(moId) +
                                     "! For explanation, see WARN above.")

    def create_agent_objects(self, objectList):
        """This keyword is used to create nasda agent objects to oes.

        @objectList:Format of list[list[]...]: fqdn, attribute(optional)
        """
        relationships = []
        for obj in objectList:
            relationships.append([obj[0], obj[0], 'AGENT'])
        self.create_objects(objectList)
        self.createRelationships(relationships)

    def delete_agent_relationships(self, objectList):
        relationships = []
        for obj in objectList:
            relationships.append([obj[0], obj[0], 'AGENT'])
        self.deleteRelationships(relationships)

    def check_managed_objects_exist(self, moList, fail_on_first_error=True, no_warns=False):
        LOGGER.trace("Check managed objects exist called with parameters\n" + str(moList))
        if type(moList) != type(list()):
            raise AttributeError("moList must be list of DNs, e.g. ['PLMN-TEST', 'PLMN-TEST/OMS-1'].")
        rc = 0
        error = False
        for mo in moList:
            moId, parameters = self._get_object_info(mo)
            response = self._getMO(moId)
            rc = self._verifyResponse(response, False, no_warns)
            if (not error) and rc != 0:
                error = True
                if fail_on_first_error:
                    raise AssertionError("NASDA Error(s) occurred for DN " + str(moId) +
                                         " For explanation, see WARN(s) above.")
        if error == True:
            return False
        else:
            return True

    def delete_all_objects(self, object_list, mode="all_in_one"):
        """This keyword is used to delete the given object_list and its all child objects.
        For not existing objects , this keyword will ingnore them .
        @object_list:Format of list[list[]...]: fqdn, release, attribute(optional)
        Example value: [["PLMN-PLMN/MGW-1001", "U5.0EP1",{"directIntegration":True}],["PLMN-PLMN/MGW-1001/MPCM-1", "U5.0EP1"]]
        @adaptation_id:such as "NOKMGW" or "NOKBSC"
        e.g. If BSC-1 ,BSC-1/BCF-1 ,BSC-1/ACP-1 are all in database . If we only input BSC-1 , then all the sub objects(BSC-1/BCF-1 ,BSC-1/ACP-1) will be deleted.

        """
        nasda_object_list = object_list[:]
        for nasda_object in object_list:
            nasda_check_result = self._check_nasda_objects_existing([nasda_object])
            if not nasda_check_result:
                nasda_object_list.remove(nasda_object)

        if nasda_object_list:
            nasda_all_object_list = nasda_object_list[:]
            for obj in nasda_object_list:
                if type(obj) is list:
                    sub_obj = self.getRelatedMOsTree(obj[0])
                else:
                    sub_obj = self.getRelatedMOsTree(obj)
                for i in sub_obj:
                    sub_object = [i, {}]
                    nasda_all_object_list.append(sub_object)
            self.delete_objects(nasda_all_object_list, mode)

    def _check_nasda_objects_existing(self, object_list):
        not_existing_nasda_objects = []
        for obj in object_list:
            if isinstance(obj, basestring):
                check_result = self.check_MOs_exist([obj], False)
            else:
                check_result = self.check_MOs_exist([obj[0]], False)
            attr_check = True
            if check_result and len(obj) == 3:
                attr_check = self._check_nasda_object_attribute(*obj)
            if (not check_result or not attr_check):
                not_existing_nasda_objects.append(obj)
        if not_existing_nasda_objects:
            LOGGER.info("the following objects do not exist in the nasda database : %s" % not_existing_nasda_objects)
            return False
        else:
            LOGGER.info("all the nasda objects exist the nasda database:%s" % object_list)
            return True

    def check_object_attribute(self, object_list):
        """This keyword is used to check whether objects' attribute is right as we expect.

        @object_list:Format of list[list[]...]: fqdn, release, parameter(attribute)
        Example value: [["PLMN-PLMN/MGW-1001", "U5.0EP1",{"directIntegration":True}],["PLMN-PLMN/MGW-1001/MPCM-1", "U5.0EP1"]]
        Then nasda object ["PLMN-PLMN/MGW-1001", "U5.0EP1",{"directIntegration":True}] will be checked in nasda database.
        And configurator object ["PLMN-PLMN/MGW-1001/MPCM-1", "U5.0EP1"]] will be checked in configurator database
        """
        wrong_attribute_objects = []
        if object_list:
            for obj in object_list:
                result = self._check_nasda_object_attribute(*obj)
                if not result:
                    wrong_attribute_objects.append(obj)
        if not wrong_attribute_objects:
            LOGGER.info("All the objects' attributes are correct")
            return True
        else:
            LOGGER.info("The following objects' attributes are not correct : %s" % wrong_attribute_objects)
            return False

    def _check_nasda_object_attribute(self, moId, release, attribute={}):
        attr_actual = self.get_mo_attributes(moId)
        checkAgent = True
        if release:
            attribute['version'] = release
        for (key, value) in attribute.items():
            if key.lower() != 'isagent':
                attribute[key] = str(value).lower()
        for key in attribute:
            if key.lower() == 'isagent':
                checkAgent = self._check_is_agent_object(moId, attribute[key])
                attribute.pop(key)
                break
        if attr_actual is None:
            LOGGER.debug("The attributes of object %s can not be gotten." % moId)
        else:
            for (key, value) in attr_actual.items():
                attr_actual[key] = str(value).lower()
        LOGGER.info("For object %s ,expect attributes is %s ,actual attribute is %s" % (moId, attribute, attr_actual))
        if attribute != attr_actual:
            return False
        elif checkAgent == False:
            LOGGER.info("The assign-self-agent check result is False.")
            return False
        else:
            return True

    def _check_is_agent_object(self, moId, expect_is_agent=True):
        agent_obj_list = self.getRelatedMOsTree(moId, 'AGENT')
        if (moId in agent_obj_list) and (expect_is_agent is True):
            return True
        elif (moId not in agent_obj_list) and (expect_is_agent is False):
            return True
        else:
            return False

    def _create_root_objects(self, object_list):
        rootList = []
        removedRootList = []
        for obj in object_list:
            if obj[0].split("/")[0] not in rootList:
                rootList.append(obj[0].split("/")[0])
            if "/" not in obj[0]:
                removedRootList.append(obj[0])
        rootList = list(set(rootList) - set(removedRootList))
        for root in rootList:
            #c, v = self.nasda.get_mo_metaclass_and_version(root)
            print "Create Root Object: %s" % root
            if not self._check_nasda_objects_existing([[root]]):
                try:
                    moId, parameters = self._get_object_info(root)
                    metaClass, metaVersion = self.get_mo_metaclass_and_version(moId)
                    response = self._createMO(moId, metaClass, metaVersion, parameters)
                    rc = self._verifyResponse(response)
                    if rc != 0:
                        LOGGER.warn("Create Root Object failed: %s" % root)
                except Exception, err:
                    LOGGER.warn("Create Root Object failed: %s" % root)

    #----------------------------------------------------------

    def create_update_delete_objects(self, object_list, fail_on_first_error=True):
        '''
        Creates, updates or deletes objects.
        @param object_list: List of objects to be created, updated or deleted
        Format : object_list[[fqdn,{parameters},operation=""]...]:
        Where:
        fqdn == e.g. PLMN-PLMN/RNC-123
        {parameters} == dictionary with key-value pairs of object parameters
        operation == 'create' or 'update' or 'delete', optional (DEFAULT=='create')

        Example value: [["PLMN-PLMN/RNC-parent2", {}, "delete" ],["PLMN-PLMN/RNC-parent2/WBTS-parent", {}], ["PLMN-PLMN/RNC-parent2/WBTS-parent/AXC-child", {"mainHost":"agent", "externalKey":"nwi3system"}, "create"], ["PLMN-PLMN/RNC-oma"]]

        @param fail_on_first_error: When 'True' (default) fails on first error,
                                    'False' fails on errors after every object is tried
                                    'None' = do not fail on any error.
        @raise AssertionError: When there were errors in operations

        '''
        LOGGER.trace(
            "NasdaOperations.create_update_delete_objects called with parameters " + str(self) + " " + str(object_list))
        rc = 0
        error = False
        moid = None
        for obj in object_list:
            if type(obj) != type(list()):
                raise TypeError(
                    "\nObject_list not well formatted, must be list of lists, e.g. [['PLMN-TEST'],['PLMN-TEST/OMS-1']]. Current object_list = " + str(
                        object_list) + "\n")
        for objectdata in object_list:
            if len(objectdata) > 0 and len(objectdata[0]) > 0:
                moid = objectdata[0]
            else:
                raise AttributeError("FQDN must be defined")
            parameters = None
            if len(objectdata) > 1:
                parameters = objectdata[1]
                #print "*DEBUG " + str(parameters)
            operation = ""
            if len(objectdata) > 2:
                operation = objectdata[2]
                #print "*DEBUG " +  str(operation)
            try:
                mc, mv = self.get_mo_metaclass_and_version(moid)
                if mc is not None and mv is not None:
                    if operation.lower() == 'delete':
                        response = self._deleteMO(moid)
                        rc = self._verifyResponse(response)
                    elif operation.lower() == 'update':
                        response = self._updateMO(moid, mc, mv, parameters)
                        rc = self._verifyResponse(response)
                    else:
                        response = self._createMO(moid, mc, mv, parameters)
                        rc = self._verifyResponse(response)
                else:
                    raise AssertionError(
                        "*ERROR* NASDA.create_update_delete_objects: _get_mo_metaclass_and_version returned None: Cannot find metadata for object '" + str(
                            moid) + "'")
            except Exception as e:
                raise AssertionError("*ERROR* NASDA.create_update_delete_objects: exception occurred: " + str(e))
            if rc != 0:
                error = True
                if fail_on_first_error:
                    raise AssertionError("*ERROR* NASDA Error occurred for object: " + str(
                        objectdata) + "! For explanation, see WARN above.")
            else:
                if operation.lower() == 'delete':
                    try:
                        self.CreatedObjects.remove(moid)
                    except ValueError:
                        pass
                elif len(operation) == 0 or operation.lower() != 'update':  # Create
                    self.CreatedObjects.append(moid)
        if error == True:
            if fail_on_first_error != None:
                raise AssertionError("*ERROR* NASDA Error(s) occurred! For explanation, see WARN(s) above.")
            else:
                return 1
        else:
            return 0

    def delete_objects(self, object_list, mode="all_in_one"):
        '''
        Forces 'delete' operation to all objects in 'object_list'.
        Can use same 'object_list' that was used to create objects.
        @param object_list: uses same kind of object list as create_update_delete_objects
        @param mode: 'all_in_one': one delete request, raises exception (fast, does not delete objects after first failure)
                     'do_not_fail': multiple delete requests, does not raise exception if error(s) occur (slow, tries to delete other objects after first failure)
                     any other value: multiple delete requests, raises exception if error(s) occur (slow, tries to delete other objects after first failure)
        @raise AssertionError: when object deletion fails
        '''
        LOGGER.trace("NasdaOperations.delete_objects called with parameters " + str(self) + " " + str(object_list))
        moIdList = []
        rc = 0
        for o in object_list:
            if len(o) > 0 and o[0] not in moIdList:
                moIdList.append(o[0])
        if mode == "all_in_one":
            LOGGER.debug("Deleting objects: " + str(moIdList))
            rsp = self._deleteMOs(moIdList)
            self._verifyResponse(rsp, True)
        else:
            moIdList.sort(self._compare_dn_depth)
            for m in moIdList:
                LOGGER.debug("Deleting object: " + str(m))
                rsp = self._deleteMO(m)
                if mode != "do_not_fail":
                    rc = self._verifyResponse(rsp)
                    if rc != 0:
                        raise AssertionError(
                            "*ERROR* NASDA.delete_objects: NASDA error(s) occurred! For explanation, see WARN(s) above.")
                else:
                    self._verifyResponse(rsp, False, True)

    def cleanup(self):
        '''
        Convenience method to delete all successfully created objects within this instance
        of NasdaOperations.
        '''
        self.CreatedObjects.sort(self._compare_dn_depth)
        LOGGER.debug("NasdaOperations.cleanup deleting objects: " + str(self.CreatedObjects) + "\n")
        for moid in self.CreatedObjects[:]:
            response = self._deleteMO(moid)
            try:
                if self._verifyResponse(response) == 0:
                    try:
                        self.CreatedObjects.remove(moid)
                    except ValueError:
                        pass
            except:
                LOGGER.debug("ERROR: Invalid NASDA response.")
        if len(self.CreatedObjects) > 0:
            LOGGER.warn("Following object(s) could not be removed: " + str(self.CreatedObjects))
        else:
            LOGGER.debug("Cleanup executed successfully.")

    def printMetadata(self):
        '''
        Prints out NASDA metadata information, useful for debugging purposes
        '''
        rsp = self._getMetadata()
        result = rsp.get_element_result()
        modefs = result.get_element_managedObjectDefs()
        modef = modefs.get_element_managedObjectDef()
        for mo in modef:
            LOGGER.info("class: %s version: %s" % (mo.get_attribute_metaClass(), mo.get_attribute_metaVersion()))
            ps = mo.get_element_pDef()
            if hasattr(ps, '__contains__'):
                for p in ps:
                    LOGGER.info("         %s (%s)" % (p.get_attribute_name(), p.get_attribute_type()))

    def get_metadata_objects_by_metaclass(self, metaclass=None):
        '''
        Get list of NASDA metadata objects by given meta class.
        @param metaclass: meta class where to search for objects, can be either full length meta class name
        e.g. 'com.nsn.netact.nasda.interfaces', or shortened by following way:
        e.g. 'interfaces', 'common', or 'connectivity'
        @return: list of found objects e.g. ['WSETC', 'MRC', 'SITE', 'MR', 'SITEC', 'WSET']
        or empty list if nothing is found
        '''
        olist = []
        if not metaclass:
            raise AttributeError("Meta class must be defined")
        if '.' not in metaclass:
            metaclass = NEC.NASDA_ID_PREFIX + '.' + metaclass
        alist = self._getMetadata().get_element_result().get_element_managedObjectDefs().get_element_managedObjectDef()
        if alist is None:
            raise AssertionError("Nasda metadata gotten failed!")
        for a in alist:
            if metaclass in a.get_attribute_metaClass():
                olist.append(a.get_attribute_metaClass()[a.get_attribute_metaClass().find(':') + 1:])
        return olist

    def get_mo_metaclass_and_version(self, moId):
        '''
        Get Managed Object's metaClass and metaVersion from NASDA.
        @param moId: MOID or object e.g. "PLMN-PLMN/OMS-1" or "OMS"
        @return: metaClass, metaVersion e.g. "com.nsn.netact.nasda.connectivity:OMS","1.0", None if metaClass or version found.
        '''
        rsp = self._getMetadata()
        result = rsp.get_element_result()
        modef = result.get_element_managedObjectDefs().get_element_managedObjectDef()
        mid = self._parseMONameFromDN(moId)  # "PLMN-PLMN/OMS-1" -> OMS

        for mo in modef:
            mc = mo.get_attribute_metaClass()
            if mc[mc.rfind(NEC.NASDA_ID_SEPARATOR) + 1:] == mid:
                return mc, mo.get_attribute_metaVersion()
        return None, None

    def get_mo_attributenames_from_metadata(self, moId):
        '''
        Returns list of supported attribute names of NASDA managed object from metadata.
        @param moId: MOID or object e.g. "PLMN-PLMN/OMS-1" or "OMS"
        @return: List of MO attribute names. e.g. ['version','directintegration']
        '''
        rsp = self._getMetadata()
        result = rsp.get_element_result()
        modef = result.get_element_managedObjectDefs().get_element_managedObjectDef()
        mid = self._parseMONameFromDN(moId)  # e.g. "PLMN-PLMN/OMS-1" -> OMS
        attr_list = []
        for mo in modef:
            mc = mo.get_attribute_metaClass()
            if mc[mc.rfind(NEC.NASDA_ID_SEPARATOR) + 1:] == mid:
                ps = mo.get_element_pDef()
                if hasattr(ps, '__contains__'):
                    for p in ps:
                        attr_list.append(p.get_attribute_name())
        return attr_list

    def get_mo_attributes(self, moId, attribute=None):
        '''
        Returns a dictionary of inserted attributes and attribute values of NASDA managed object.
        Can also be used to fetch current value of a single attribute.
        @param moId: e.g. "PLMN-PLMN/OMS-1"
        @param attribute: attribute to be checked, e.g. "version"
        @return: Dictionary of MO attributes with values. e.g. {'version':'RN6.0',...}
            Dictionary is empty if there were no attributes.
            Returns attribute value if param attribute is given. Returns empty string if
            attribute doesn't have a value in database.
        @raise AssertionError: If attribute parameter given and it is not valid attribute
            according to object's metadata, or any other NASDA error occurs.
        '''
        LOGGER.trace("NasdaOperations.get_mo_attributes() called with moId: %s" % moId)
        response = self._getMO(moId)
        result = response.get_element_result()
        aDict = None
        resDict = dir(result)
        if resDict.__contains__('BatchItemMOResult'):
            batch = result.get_element_batchItemMOResult()
            for item in batch:
                if item.get_element_errorCause() == None:
                    pList = item.get_element_managedObject().get_element_p()
                    aDict = {}
                    if pList != None:
                        for p in pList:
                            aDict[p.get_attribute_name()] = p
                else:
                    LOGGER.warn("NASDA Error occurred when fetching parameter value(s) for object %s!: %s\n%s" \
                                % (moId, item.get_element_errorCode(),
                                   item.get_element_errorCause()[:item.get_element_errorCause().find('\n')]))
                    raise AssertionError(
                        "*ERROR* NASDA Error occurred when fetching parameter value(s) for object %s!: %s\n%s" \
                        % (moId, item.get_element_errorCode(),
                           item.get_element_errorCause()[:item.get_element_errorCause().find('\n')]))
                    break
            if attribute != None:
                if attribute in aDict:
                    return aDict[attribute]
                else:
                    if attribute in self.get_mo_attributenames_from_metadata(moId):
                        return ""  # valid attribute without value in NASDA
                    else:
                        # invalid attribute not found in NASDA metadata
                        LOGGER.warn("Invalid attribute: %s! Not found from NASDA metadata." % attribute)
                        raise AssertionError(
                            "*ERROR* Invalid attribute: '%s' Not found for object %s from NASDA metadata." % (
                                attribute, moId))

        LOGGER.debug("NasdaOperations.get_mo_attributes()MO %s attributes:\n%s" % (moId, str(aDict)))
        return aDict

    def get_hostname_by_dn(self, dn, interface='EM'):
        '''
        Get Hostname by DN

        @param dn: managed object FQDN e.g. "PLMN-PLMN/RNC-1"
        @param interface: interface object class e.g. "EM", "HTTP", "MML"
        @return: hostname of object (hostName attribute value of EM-object under given dn)
        Raises exception if hostname not found.
        '''
        if not dn:
            raise AttributeError("Parameter dn must be defined")
        MOP = self._createMOPathFromDN(dn)
        try:
            MOQ = self.get_objects_with_MOQuery('any::' + MOP[1:] + '/child::' + interface + '[@hostName]')
        except Exception as e:
            raise AssertionError(
                "*ERROR* MOQuery raised exception when trying to find '%s' interface for object '%s' from NASDA database." % (
                    interface, dn))
        if MOQ == []:
            raise AssertionError(
                "*ERROR* MOQuery did not find hostname ('%s'-object with hostName attribute) for object '%s' from NASDA database." % (
                    interface, dn))
        hostname = self.get_mo_attributes(MOQ[0], 'hostName')
        return hostname

    def getRelatedMOsTree(self, moId, relationship="CHILD"):
        '''
        Get Related MOs Tree

        @param moId: managed object id e.g. "PLMN-PLMN"
        @param relationship: relationship of returned objects. Values: "CHILD" (default) or "PARENT"
        @return: List of related object moIds e.g. ['PLMN-PP1/OMS-1', 'PLMN-PP1/OMS-1/NWI3-1', 'PLMN-PP1/OMS-1/NWI3-2', 'PLMN-PP1/RNC-1'].
        Returns empty list if moId not found.
        '''
        LOGGER.trace("NasdaOperations.getRelatedMOsTree called with moId: %s  relationship: %s " % (moId, relationship))
        output = []
        rsp = self._getRelatedMOs(moId, relationship)
        result = rsp.get_element_result()
        resultSeq = result.get_element_batchItemMOLiteSequenceResult()
        for res in resultSeq:
            if dir(res).__contains__('_moLite'):
                moLiteList = res.get_element_moLite()
                #print moLiteList
                for moLite in moLiteList:
                    moId = moLite.get_attribute_moId()
                    output.append(moId)
                    if relationship != "AGENT" and relationship != "AGENT_REVERSED":
                        subtree = self.getRelatedMOsTree(moId, relationship)
                        output = output + subtree
        return output

    def get_objects_with_MOQuery(self, query, variableBindings={}):
        '''
        Get Objects With MOQuery

        @param query: MOQuery string, e.g. "any::OMS"
                      See examples at https://confluence.inside.nokiasiemensnetworks.com/display/CMOP/NASDA+MOQuery
        @param variableBindings: Variable binding for parameterized queries
        @return: List of found objects e.g. ['PLMN-123/OMS-1', 'PLMN-PP1/OMS-3', 'PLMN-PP2/OMS-4'].
        Returns empty list if no objects found.
        '''
        rsp = self._query_molites(query, variableBindings)
        result = rsp.get_element_result()
        moLiteList = []
        if dir(result).__contains__('_moLite'):
            moLite = result.get_element_moLite()
            if moLite:
                for i in moLite:
                    moLiteList.append(i.get_attribute_moId())
                LOGGER.debug("Found objects matching %s%s: %s" % (query, variableBindings, moLiteList))
            else:
                LOGGER.debug("No objects matching %s%s were found." % (query, variableBindings))
        return moLiteList

    def get_objects_by_class_and_release(self, objectclass='*', release=None):
        '''
        Get Objects by Class and Release from NASDA

        @param objectclass: (mandatory if release is specified, otherwise optional) object class e.g. "OMS"
        @param release: (optional) release e.g. "RNO1.0_1.0"
        @return: List of found objects e.g. ['PLMN-123/OMS-1', 'PLMN-PP1/OMS-3', 'PLMN-PP2/OMS-4'].
        Returns empty list if no objects found.
        '''
        LOGGER.debug(
            "NasdaOperations.get_objects_by_class_and_release called with parameters: %s %s" % (objectclass, release))
        moLiteList = []
        query = 'any::' + objectclass
        if release:
            query += '[ @' + 'version' + ' like "' + release + '" ]'
        rsp = self._query_molites(query)
        try:
            result = rsp.get_element_result()
        except:
            raise AssertionError("*ERROR* NASDA Error(s) occurred for object class " + str(
                objectclass) + ". For explanation, see WARN(s) above.")
        if dir(result).__contains__('_moLite'):
            moLite = result.get_element_moLite()
            if moLite:
                for i in moLite:
                    moLiteList.append(i.get_attribute_moId())
                LOGGER.debug("Found objects matching %s%s: %s" % (
                    objectclass, ('' if not release else ' ' + release), moLiteList))
            else:
                LOGGER.debug(
                    "No objects matching %s%s were found." % (objectclass, ('' if not release else ' ' + release)))
        return moLiteList

    def get_upload_agents(self, DN_filter=None, release=None):
        '''
        Get Upload Agent Objects from NASDA

        @param DN_filter: object for which to find the upload agent
        syntax is FQDN, SDN or class e.g. "PLMN-1/RNC-1", "RNC-1" or "RNC"
        @param release: (optional) release of the object e.g. "RN6.0_2.0"
        leave DN_filter empty to get all upload agents in system, or give just release to get all upload agents hosting object of that version.
        e.g. get_upload_agents() or get_upload_agents(None, 'WN6.0')
        Execution speed in order of use of DN_filter: FQDN (fastest), SDN, object class, None (slowest)
        @return: List of found agent objects e.g. ['PLMN-123/OMS-1', 'PLMN-PP1/OMS-3', 'PLMN-PP2/OMS-4'].
        Returns empty list if no objects are found.
        '''
        LOGGER.debug("NasdaOperations.get_upload_agents called with parameters: %s" % DN_filter)

        if DN_filter != None:
            objectlist = self.getRelatedMOsTree(DN_filter, 'AGENT')
            LOGGER.debug("Direct agent object = %s" % objectlist)
            # If 'DN_filter' is not a direct DN
            if objectlist:
                return objectlist
            elif not objectlist and DN_filter.find('/') == -1:
                LOGGER.debug(
                    "Direct agent object was not found, so trying to find other objects matching filter %s" % DN_filter)
                oclass = self._parseMONameFromDN(DN_filter)
                olist = self.get_objects_by_class_and_release(oclass, release)
                for DN in olist:
                    # DN_end = 'RNC-124', DN = 'PLMN-1/RNC-124'
                    DN_end = DN[DN.find(DN_filter):]
                    # if '-' is not found in DN_filter it is assumed to be object class
                    if DN_filter == DN_end or (DN_filter.find('-') == -1 and DN_filter in DN):
                        objectlist.append(DN)
            elif DN_filter.find('/') != -1:
                LOGGER.debug("Could not find any agent objects with DN %s" % DN_filter)
        else:
            LOGGER.debug(
                "Warning: As DN_filter was not specified, searching through whole object tree, this can take a long time!")
            objectlist = self.getRelatedMOsTree('<ROOT>')
        agentlist = []
        agent = None
        duplicate = 0
        for DN in objectlist:
            if DN_filter:
                if DN.rfind(DN_filter) > DN.rfind('/'):
                    if release:
                        if self.get_mo_attributes(DN, 'version') == release:
                            agent = self.getRelatedMOsTree(DN, 'AGENT')
                    else:
                        LOGGER.debug("Found matching object: %s" % DN)
                        agent = self.getRelatedMOsTree(DN, 'AGENT')
                    if agent:
                        for a in agentlist:
                            if a.find(agent[0]) != -1:
                                duplicate = 1
                        if duplicate == 0:
                            agentlist.append(agent[0])
                        duplicate = 0
            else:
                #If user wants to get all agents in system
                olist = self.getRelatedMOsTree(DN, 'CHILD')
                for o in olist:
                    if release:
                        o_attributes = self.get_mo_attributenames_from_metadata(o)
                        if 'version' in o_attributes:
                            if self.get_mo_attributes(o, 'version') == release:
                                agent = self.getRelatedMOsTree(o, 'AGENT')
                    else:
                        agent = self.getRelatedMOsTree(o, 'AGENT')
                    if agent:
                        for a in agentlist:
                            if a.find(agent[0]) != -1:
                                duplicate = 1
                        if duplicate == 0:
                            agentlist.append(agent[0])
                        duplicate = 0
        if not agentlist:
            LOGGER.debug("Could not find any agent objects.")
        return agentlist

    def get_upload_agent_reversed(self, FQDN, objectfilter=None):
        '''
        Get Upload Agent Reversed

        @param FQDN: FQDN of upload agent object for which to find related objects e.g. "PLMN-1/OMS-1"
        @param objectfilter: (optional) object filter of the related object(s), can be object class or
                             instance, e.g."RNC" or "RNC-181"
        leave objectfilter empty to get all related objects (may include also upload agent itself)
        @return: List of found NASDA objects e.g. ['PLMN-PP1/OMS-1', 'PLMN-PP1/RNC-1', 'PLMN-PP1/RNC-1/WBTS-1'].
        Returns empty list if no objects are found.
        '''
        objs = []
        all_objs = self.getRelatedMOsTree(FQDN, 'AGENT_REVERSED')
        if objectfilter:
            for o in all_objs:
                # DN_end = 'RNC-124', o = 'PLMN-1/RNC-124'
                DN_end = o[o.find(objectfilter):]
                if DN_end.find('/') == -1 and objectfilter in DN_end:
                    objs.append(o)
        else:
            objs = all_objs
        return objs

    def check_MOs_exist(self, MOList, fail_on_first_error=True, no_warns=False):
        '''
        Check if listed MOs exist in NASDA database.
        (accepts also same list format as used for create_update_delete_objects)

        @param MOList: ['MoId1', 'MoId2', 'MoId3',...] or [[fqdn,{parameters},operation=""]...]:
            examples ['PLMN-NAT22', 'PLMN-NAT22/RNC-1667', 'PLMN-NAT22/OMS-1665'] or
                    [['PLMN-NAT22',{}, "delete"],['PLMN-NAT22/RNC-1667']]
        @param fail_on_first_error: if True, checking will stop on first error
        @param no_warns: if True, checking will not print *WARN* messages on report
        @raise AttributeError: if MOList is not properly formatted.
        @raise AssertionError: if NASDA error occurs.
        @returns True if no errors occurred, otherwise False
        '''
        LOGGER.trace("NasdaOperations.check_MOs_exist called with parameters\n" + str(self) + " " + str(MOList))
        if type(MOList) != type(list()):
            raise AttributeError(
                "\MOList not well formatted, must be list of DNs, e.g. ['PLMN-TEST', 'PLMN-TEST/OMS-1']. Current MOList = " + str(
                    MOList) + "\n")
        elif len(MOList) == 0:
            raise AttributeError(
                "\MOList empty, must be list of DNs, e.g. ['PLMN-TEST', 'PLMN-TEST/OMS-1']. Current MOList = " + str(
                    MOList) + "\n")
        rc = 0
        error = False
        for MO in MOList:
            if type(MO) == type(list()):
                if len(MO) == 0:
                    raise AttributeError(
                        "List should contain DN, example [['PLMN-123']...]. Current MOList: " + str(MOList) + " \n")
                elif len(MO[0]) <= 3:
                    raise AttributeError("DN length too short!: length of " + str(MO[0]) + " <= 3")
                response = self._getMO(MO[0])
                rc = self._verifyResponse(response, False, no_warns)
            else:
                if len(MO) <= 3:
                    raise AttributeError("DN length too short!: length of " + str(MO) + " <= 3")
                else:
                    response = self._getMO(str(MO))
                    rc = self._verifyResponse(response, False, no_warns)
            if rc != 0:
                error = True
                if fail_on_first_error:
                    raise AssertionError(
                        "*ERROR* NASDA Error(s) occurred for DN " + str(MO) + " For explanation, see WARN(s) above.")
        if error == True:
            return False
        else:
            return True

    def createRelationships(self, relationshipList, fail_on_first_error=True):
        '''
        Create list of relationships between two objects.

        @param relationshipList: [[sourceMoId, targetMoId, relationshipId],...]
        example [[PLMN-NAT22/RNC-1667','PLMN-NAT22/OMS-1665','AGENT']]
        @raise AttributeError: if relationships in relationshipList parameter doesn't contain necessary items.
        @raise AssertionError: if NASDA error occurs.
        @raise TypeError: if relationshipList not well formatted
        '''
        LOGGER.trace(
            "NasdaOperations.createRelationships called with parameters\n" + str(self) + " " + str(relationshipList))
        if type(relationshipList) != type(list()):
            raise AttributeError(
                "\relationshipList not well formatted, must be list of lists, e.g. [['PLMN-TEST'],['PLMN-TEST/OMS-1']]. Current relationshipList = " + str(
                    relationshipList) + "\n")
        for relationship in relationshipList:
            if type(relationship) != type(list()):
                raise TypeError(
                    "\relationshipList not well formatted, must be list of lists, e.g. [['PLMN-TEST'],['PLMN-TEST/OMS-1']]. Current object_list = " + str(
                        relationshipList) + "\n")

        smoid = None
        tmoid = None
        rc = 0
        error = False
        for relationship in relationshipList:
            if len(relationship) != 3:
                raise AttributeError("Relationship must contain [sourceMoId, targetMoId , relationshipId]!")
            if len(relationship[0]) > 0 and len(relationship[1]) > 0:
                smoid = relationship[0]
                tmoid = relationship[1]
            else:
                raise AttributeError("Source and target MOId must be defined!")
            rid = None
            if len(relationship[2]) > 0:
                rid = relationship[2]
            else:
                raise AttributeError("Relationship Id must be defined!")

            response = self._createRelationship(smoid, tmoid, rid)
            rc = self._verifyResponse(response)
            if rc != 0:
                error = True
                if fail_on_first_error:
                    raise AssertionError("*ERROR* NASDA Error(s) occurred for relationship: " + str(
                        relationship) + "! For explanation, see WARN(s) above.")

        if error == True:
            raise AssertionError("*ERROR* NASDA Error(s) occurred! For explanation, see WARN(s) above.")

    def deleteRelationships(self, relationshipList, fail_on_first_error=True):
        '''
        Delete list of relationships between two objects.

        @param relationshipList: [[sourceMoId, targetMoId, relationshipId],...]
        example [[PLMN-NAT22/RNC-1667','PLMN-NAT22/OMS-1665','AGENT']]
        @raise AttributeError: if relationships in relationshipList parameter doesn't contain necessary items.
        @raise AssertionError: if NASDA error occurs.
        @raise TypeError: if relationshipList not well formatted
        '''
        LOGGER.trace(
            "NasdaOperations.deleteRelationships called with parameters\n" + str(self) + " " + str(relationshipList))
        if type(relationshipList) != type(list()):
            raise AttributeError(
                "\relationshipList not well formatted, must be list of lists, e.g. [['PLMN-TEST'],['PLMN-TEST/OMS-1']]. Current relationshipList = " + str(
                    relationshipList) + "\n")
        for relationship in relationshipList:
            if type(relationship) != type(list()):
                raise TypeError(
                    "\relationshipList not well formatted, must be list of lists, e.g. [['PLMN-TEST'],['PLMN-TEST/OMS-1']]. Current object_list = " + str(
                        relationshipList) + "\n")

        smoid = None
        tmoid = None
        rc = 0
        error = False
        for relationship in relationshipList:
            if len(relationship) != 3:
                raise AttributeError("Relationship must contain [sourceMoId, targetMoId , relationshipId]!")
            if len(relationship[0]) > 0 and len(relationship[1]) > 0:
                smoid = relationship[0]
                tmoid = relationship[1]
            else:
                raise AttributeError("Source and target MOId must be defined!")
            rid = None
            if len(relationship[2]) > 0:
                rid = relationship[2]
            else:
                raise AttributeError("Relationship Id must be defined!")

            response = self._deleteRelationship(smoid, tmoid, rid)
            rc = self._verifyResponse(response)
            if rc != 0:
                error = True
                if fail_on_first_error:
                    raise AssertionError("*ERROR* NASDA Error(s) occurred! For explanation, see WARN(s) above.")

        if error == True:
            raise AssertionError("*ERROR* NASDA Error(s) occurred! For explanation, see WARN(s) above.")

    def get_hostnames_by_objectclass_and_release(self, objectClass, release, interface='EM'):
        '''
        Get hostNames of given objectClass and release.

        @param objectClass: e.g. RNC
        @param release: Release e.g. RN6.0_1.0
        @param interface: Optional interface component where hostName attribute is (default='EM')
        @return: A dictionary containing object DNs and hostNames {<object DN>: <hostName>,...}
            Empty dictionary if no hosts found
        @raise AssertionError: If MO query fails e.g. non-existing object class
        '''
        LOGGER.trace(
            "NasdaOperations.get_hostnames_by_objectclass_and_release called with parameters\n" + objectClass + " " + release)

        resultDict = {}
        hostList = []
        query = "any::" + objectClass + "[@version = \"" + release + "\"] / child::" + interface + "[@hostName]"
        try:
            hostList = self.get_objects_with_MOQuery(query)
        except Exception as e:
            raise AssertionError("*ERROR* MOQuery raised exception when trying to find objects \
                with class '%s', release '%s' and interface '%s' from NASDA database.\
                \nQuery: %s \nException: %s" % (objectClass, release, interface, query, str(e)))
        if len(hostList) > 0:
            LOGGER.trace("Query returned host(s): %s" % str(hostList))
            for host in hostList:
                parentList = []
                moPath = self._createMOPathFromDN(host)
                query = "any::" + moPath[1:] + " / parent::" + objectClass
                try:
                    parentList = self.get_objects_with_MOQuery(query)
                    LOGGER.trace("Parent: %s" % str(parentList))
                except Exception as e:
                    raise AssertionError("*ERROR* MOQuery raised exception when querying \
                        '%s' from NASDA database.\n%s" % (query, str(e)))
                hostName = self.get_mo_attributes(host, NEC.HTTP_HOST_NAME)
                LOGGER.trace("%s %s: %s " % (parentList[0], NEC.HTTP_HOST_NAME, hostName))
                resultDict[parentList[0]] = hostName
        else:
            LOGGER.trace("No hosts found.")
        LOGGER.trace("NasdaOperations.get_hostnames_by_objectclass_and_release returns:%s\n" % str(resultDict))
        return resultDict

    def _get_object_info(self, obj):
        if isinstance(obj, basestring):
            return obj, {}
        if type(obj) is not list:
            raise AssertionError("Object should be configured as a list or string: %s" % str(obj))
        moId = obj[0]
        parameters = {}
        if len(obj) == 2 and isinstance(obj[1], dict):
            parameters = obj[1]
        elif len(obj) == 2 and isinstance(obj[1], basestring):
            parameters['version'] = obj[1]
        elif len(obj) > 2 and isinstance(obj[2], dict):
            parameters = obj[2]
            parameters['version'] = obj[1]
        return moId, parameters


if __name__ == '__main__':
    # Correct metaClass for MO e.g. OMS can be found also with SQL-clause: select OC_ADAPTATION from NASDA_OBJECT_CLASS where OC_ABBREVIATION = 'OMS';

    #NASDAHOST = "clab036lb.netact.nsn-rdnet.net"    # "makepeace.netact.noklab.net"
    #wsdlLocationURL = "http://"+NASDAHOST+ "/netact/oss/nasda/ws-api/NasdaWSPersistencyServiceSOAP?wsdl"
    NASDAHOST = "clab294node04.netact.nsn-rdnet.net"
    #NASDAHOST = "luciano.netact.noklab.net"
    #NASDAHOST = "casarini.netact.noklab.net"
    #NASDAHOST = "niaril.netact.noklab.net"
    #NASDAHOST = "10.41.67.205"
    #NASDAHOST = "daehoes.netact.noklab.net"

    nasda = NasdaOperations()

    nasda.setNasdaHost(NASDAHOST, 'omc', 'omc')
    #nasda.setNasdaHost(NASDAHOST, 'omc', '293--User')

    #oList6 = [["PLMN-PLMN/RNC-8080", {'version':'RN6.0_1.0'}], ["PLMN-PLMN/RNC-8080/EM-1", {'hostName':'1.2.3.4'}]]
    #nasda.create_update_delete_objects(oList6)
    #print nasda.get_hostname_by_dn('PLMN-PLMN/RNC-181', 'MML')
    #print nasda.get_hostnames_by_objectclass_and_release("RNC", "RN6.0_1.0")
    #nasda.delete_objects(oList6)

    #print nasda.get_metadata_objects_by_metaclass('com.nsn.netact.nasda.common')
    #print nasda._createMOPathFromDN('PLMN-PLMN/RNC-181/WBTS-1/WCEL-3')

    #print nasda.get_hostname_by_dn('PLMN-PLMN/RNC-181')

    #print nasda.get_upload_agents('BCUBTS')
    #print nasda.get_upload_agent_reversed('PLMN-PLMN/OMS-181', 'RNC')
    #print nasda.get_objects_with_MOQuery('')
    #print nasda.get_mo_attributenames_from_metadata('EM')
    #print nasda.get_objects_by_class_and_release('BCUBTS','R7.0')

    #print nasda.createRelationships([['PLMN-PLMN/BCUMED-1', 'PLMN-PLMN/BCUMED-1', 'AGENT']])
    #print nasda.get_upload_agents('BCUBTS')

    #print nasda.getRelatedMOsTree('<ROOT>')
    #print "Nasda operations: %s" % dir(nasda)
    #nasda.printMetadata()
    #print dir(nasda._getMetadata().get_element_result().get_element_managedObjectDefs().get_element_managedObjectDef())

    #exit(0)

    #print nasda._get_mo_metaclass_and_version('PLMN-NATE/OMS-3513')

    #list[list[]...]: fqdn, release, {parameters}, operation="", adaptationId=""
    '''
    oList=[["PLMN-NAT2"],["PLMN-NAT2/OMS-1665"],["PLMN-NAT2/RNC-1665"],
           ["PLMN-NAT2/OMS-1665/NWI3-665", {'hostName': '11.2.33.4', 'nwi3SystemId': 'NE-OMS-1665'}]]
    '''
    #oList=[["PLMNNAT3"]]

    #print "Create PLMN-NAT2 and some objects"
    #nasda.create_update_delete_objects(oList)

    #oList = [["PLMN-NAT226/OMS-6", {'version': 'RNO1.0'}], ["PLMN-NAT226/RNC-16679", {'version': 'RN6.0'}], ["PLMN-NAT226/RNC-16679/WBTS-5", {'version': 'RN6.0'}], ["PLMN-NAT226/RNC-16679/WBTS-5/WCEL-1", {'version': 'RN6.0'}]]
    #oList = [["PLMN-NAT226/RNC-666", {}]]

    #nasda.create_update_delete_objects(oList)
    #nasda._queryMoLites("PLMN-TEST/BCUBTS-11")

    #print nasda.get_mo_attributes("PLMN-TEST/BCUBTS-11",'version')

    #md = nasda._getMetadata()
    #mm = md.get_element_result().get_element_managedObjectDefs().get_element_managedObjectDef()

    #nasda.delete_objects(oList)
    '''
    oList = [["PLMN-NAT2222"], ["PLMN-NAT2222/OMS-90000"], ["PLMN-NAT2222/RNC-90000"]]
    nasda.create_update_delete_objects(oList)
    nasda.createRelationships([["PLMN-NAT2222/RNC-90000", "PLMN-NAT2222/OMS-90000", "AGENT"]])
    nasda.createRelationships([["PLMN-NAT2222/RNC-90000", "PLMN-NAT2222/OMS-90000", "AGENT"]])
    nasda.deleteRelationships([["PLMN-NAT2222/RNC-90000", "PLMN-NAT2222/OMS-90000", "AGENT"]])
    nasda.delete_objects(oList)
    '''
    #nasda.check_MOs_exist([])

    '''
    nasda.create_update_delete_objects(oList, None)

    nasda.check_MOs_exist(['PLMN-NAT226', 'PLMN-NAT266/OMS-16659', 'PLMN-NAT226/OMS-16659/NWI3-6659'], False)

    #rsp = nasda.createRelationship('PLMN-NAT226/RNC-16678','PLMN-NAT226/OMS-16659','AGENT')
    #rsp = nasda.deleteRelationship('PLMN-NAT22/RNC-1667','PLMN-NAT22/OMS-1665','AGENT')

    resp = nasda.createRelationships([['PLMN-NAT226/RNC-16678', 'PLMN-NAT226/OMS-16659', 'AGENT']])
    resp = nasda.deleteRelationships([['PLMN-NAT226/RNC-16678', 'PLMN-NAT226/OMS-16659', 'AGENT']]

    nasda.delete_objects(oList)

    #rsp = nasda.getMO('PLMN-NATE/OMS-313')

    #attr=nasda.get_mo_attributes('PLMN-NATE/OMS-313/NWI3-13')
    #print(str(attr))

    #rsp=nasda.getRelatedMOs("PLMN-NATE/OMS-313","CHILD")

    oput=nasda.getRelatedMOsTree("PLMN-NAT226", "CHILD")
    LOGGER.info("_________________________________________________")
    print oput
    #LOGGER.info("_________________________________________________")
    #oput=nasda.getRelatedMOsTree("PLMN-NAT22", "PARENT")
    #LOGGER.info("_________________________________________________")
    #print oput
    #LOGGER.info("_________________________________________________")
    oput=nasda.getRelatedMOsTree("PLMN-NAT226/OMS-16659/NWI3-6659", "PARENT")
    LOGGER.info("_________________________________________________")
    print oput
    #LOGGER.info("_________________________________________________")

    #moId, metaClass, metaVersion = nasda.getMODatas("PLMN-NAT22/OMS-1665")


    #rsp = nasda.createNwi3Interface('PLMN-NATE/OMS-313/NWI3-1', nwi3SystemId='NE-OMS-313', hostName='10.3.1.3')

    nasda.cleanup()
    '''

    exit(0)
