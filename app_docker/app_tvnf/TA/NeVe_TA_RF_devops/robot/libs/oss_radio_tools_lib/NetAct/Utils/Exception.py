#  Copyright 2014 Nokia Solution And Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


class UserHelperException(Exception):
    """
    Exception class used in UserHelper module.
    """
    pass


class DatabaseException(Exception):
    """
    Exception class for database related issue.
    """
    pass


class DatabaseConnectionException(Exception):
    """
    Exception class for database related issue.
    """
    pass


class RemoteException(Exception):
    """
    Exception class for ssh operation related issue.
    """
    pass


class RemoteTailException(Exception):
    """
    Exception class for remote tail operation related issue.
    """
    pass


class DatabaseCMException(Exception):
    """
    Exception class for CM related issue.
    """
    pass


class DatabaseFMException(Exception):
    """
    Exception class for FM related issue.
    """
    pass


class DatabasePMException(Exception):
    """
    Exception class for PM related issue.
    """
    pass


class ConfiguratorServiceException(Exception):
    """
    Exception class for Configurator Web Service related issue.
    """
    pass


class AlarmOperationServiceException(Exception):
    """
    Exception class for Alarm Operation Web Service related issue.
    """
    pass


class AlarmMonitorServiceException(Exception):
    """
    Exception class for Alarm Monitor Web Service related issue.
    """
    pass
