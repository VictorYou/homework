from robot.libraries.BuiltIn import BuiltIn
from suds.transport.https import HttpAuthenticated as Transport
from suds.client import Client

class SudsLibraryExtensions(object):
        
    def load_client_using_basic_authentication(self, url, username, password):    
        suds_lib = BuiltIn().get_library_instance("SudsLibrary")
        t = Transport(username=username, password=password)
        client = Client(url, transport=t)
        return suds_lib._add_client(client)
		
		
		
def create_soap_client_with_authentication(url, user, password):
	ext = SudsLibraryExtensions();
	return ext.load_client_using_basic_authentication(url ,user, password)