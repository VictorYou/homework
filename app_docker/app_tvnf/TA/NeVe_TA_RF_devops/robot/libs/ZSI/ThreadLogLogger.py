#encoding=utf-8
'''
This module prints thread logging information into a file 
when running Robot cases.
Created on Apr 21, 2010

@author: <a href="mailto:ENVY3@nsn.com">ENVY3</a>
'''

import logging
import sys
import datetime
import os
from robot.libraries.BuiltIn import BuiltIn
import inspect
import sys
import time
 
try:
    OUTPUT_FILE = os.environ['NWI3_ROBOT_THREADLOG']
except KeyError:
    if os.name == 'nt':
        OUTPUT_FILE = os.getenv('TMP')+"/robotThreadLog.log." + str(time.time())
    else:
        OUTPUT_FILE = "/tmp/robotThreadLog.log." + str(time.time())

LOG_FILENAME = OUTPUT_FILE

class _ThreadLogLogger():
    
    global instance
    
    def __init__(self):
        handler = logging.FileHandler(LOG_FILENAME, 'w')
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger = logging.getLogger('robotThreadLog')
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        
    def writeLog(self, msg):
        callerFunction = sys._getframe().f_back.f_code.co_name
        callerLinenro = sys._getframe().f_back.f_lineno       
        path = sys._getframe().f_back.f_code.co_filename
        splittedPath = path.split("/")
        callerFile = splittedPath.pop()

        self.logger.debug(self._formatMsg(callerFile, callerLinenro, callerFunction, msg))
        print "*DEBUG* | %s" % self._formatMsg(callerFile, callerLinenro, callerFunction, msg)
        
    def _formatMsg(self, filename, linenro, functionname, msg):
        
        if msg == None:
            message = ""
        else:
            message = msg
        
        testname = '-'
        
        try:
            testname = BuiltIn().replace_variables('${TESTNAME}')
        except:
            try:
                testname = BuiltIn().replace_variables('${SUITENAME}')
            except:
                testname = None       
                            
        if functionname != None:
            message = ":" + functionname + " | " + message
        else:
            message = " | " + message
           
        if linenro != None:
            message = ":" + str(linenro) + message

        if filename != None:
            message = filename  + message
                 
        if testname != None:
            message = testname + " | " + message
        
        message = self._getTimeStamp() + " | " + message
        
        return message
    
    def _getTimeStamp(self):
        now = time.time()
        localtime = time.localtime(now)
        milliseconds = '.%03d' % int((now - int(now)) * 1000)
        return time.strftime('%H:%M:%S', localtime) + milliseconds
    
    

_ThreadLogLogger.instance = _ThreadLogLogger()
    
def ThreadLogLogger():
    return _ThreadLogLogger.instance

