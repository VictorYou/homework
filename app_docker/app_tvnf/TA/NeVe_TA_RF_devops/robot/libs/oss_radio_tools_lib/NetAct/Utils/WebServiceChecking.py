from suds.client import Client

def check_webservice(server, path, user, pwd):
	full_url = 'http://' + server + path
	Client(url=full_url, username=user, password=pwd)