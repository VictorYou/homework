""" Robot keywords to ease up http[s] messaging """

import requests
import os
import logging

JSON_LIKE = [list, dict, str, unicode]


class requests_wrapper(object):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, base_url=''):
        self.base_url = base_url

    def send_http_no_proxy(self, method, url, params=''):
      command = "curl --noproxy '*' -X " + method + " " + url + " " +params
      print("command: {}".format(command))
      output = os.popen(command).read().strip()
      return output
      

    def send_http(self, method, url, status=None, ignore_error=False, file=None, **kwargs):
        method = method.lower()
        if method not in dir(requests):
            raise AssertionError('Invalid http method: {}'.format(method))
        request_method = requests.__dict__[method]

        data = kwargs.get('data')
        if any(isinstance(data, typ) for typ in JSON_LIKE):
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['content-type'] = 'application/json'

        auth = kwargs.get('auth')
        if isinstance(auth, list):
            kwargs['auth'] = tuple(auth)

        if file:
            f = open(file, 'rb')
            kwargs['files'] = {'file': f}

        #
        logging.basicConfig(level=logging.DEBUG)
        response = request_method(self.base_url + url, **kwargs)

        if file:
            f.close()

        if (status) and (response.status_code != int(status)):
            raise AssertionError('Received status code ({}) instead of ({})'
                                 .format(response.status_code, status)
                                 )

        if not (status or ignore_error):
            response.raise_for_status()

        return response.content
