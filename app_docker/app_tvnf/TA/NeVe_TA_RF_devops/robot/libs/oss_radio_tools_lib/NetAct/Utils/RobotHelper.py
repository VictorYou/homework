#  Copyright 2011 Nokia Siemens Networks Oyj
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

from robot.libraries.BuiltIn import BuiltIn
from collections import OrderedDict

OLDER_ROBOT_IN_USE = True
try:
    from robot.running import NAMESPACES  # Older Robot
except:
    OLDER_ROBOT_IN_USE = False
    from robot.running import context  # Robot 2.7 


class RobotHelper(object):
    '''
    RobotHelper is a helper library intended for use by other Python libraries.
    It contains convenience methods to help with the management of resources
    shared between libraries, for example database connections.

    Author: ilkka.virolainen@nsn.com
    '''

    def __init__(self):
        pass

    @staticmethod
    def get_lib_from_robot(variable, libraryName):
        """This is a wrapper keyword for Robot's `Builtin.Get Library Instance` 
        keyword. 
        But will call Robot's keyword only if given `variable` is None, i.e.
        can be used several times without need to think the overhead.
        Also logs errors in case of failure and throws exception further.
        """
        if variable is None:
            try:
                print "*INFO* %s: Getting instance of library '%s' from Robot Framework" % (__name__, libraryName)
                variable = BuiltIn().get_library_instance(libraryName)
            except RuntimeError, e:
                # Try to get library without a possible package name (if alias 
                # was used in Robot test suite).
                if libraryName.rsplit('.', 1)[0] != libraryName:
                    # libraryName consist of packages i.e. package.mylibrary
                    # try to find lib from Robot by using only "mylibrary" part.
                    _, actualLib = libraryName.rsplit('.', 1)
                    print "*INFO* %s: Could not get library instance with full package path, try to get it without package (if alias was used in Robot test suite)" % (__name__)
                    return RobotHelper.get_lib_from_robot(variable, actualLib)
                else:
                    raise AssertionError("Failed to get library '%s' from robot\n Error: %s" % (libraryName, str(e)))
            print '*INFO* Get Library %s %s' % (libraryName, str(variable))
        return variable

    @staticmethod
    def get_lib_from_robot_and_initialize_internally_on_error(variable,
                                                               libraryName,
                                                               func_obj_to_create_lib):
        """This is same as keyword `Get Lib From Robot`, but in case of library
        not found user can give function object that is used to create the object.
        """
        if variable is None:
            try:
                variable = RobotHelper.get_lib_from_robot(variable, libraryName)
            except AssertionError, e:
                print "*INFO* " + str(e) + "\n ==> Initializing " + libraryName + " internally."
                variable = func_obj_to_create_lib()
        return variable

    @staticmethod
    def _get_lib_from_robot_with_criteria(func_obj_with_criteria):
        if OLDER_ROBOT_IN_USE:
            nspace = NAMESPACES.current
            libraryDict = nspace._testlibs
            return [x.get_instance() for x in libraryDict.itervalues() if func_obj_with_criteria(x.get_instance())]            
        else:
            # This is the new way with Robot 2.7
            try:
                libraryDict = context.EXECUTION_CONTEXTS.current.namespace._testlibs
            except AttributeError:
                libraryDict = context.EXECUTION_CONTEXTS.current.namespace._kw_store.libraries
            return [x.get_instance() for x in libraryDict.itervalues() if func_obj_with_criteria(x.get_instance())]

    @staticmethod
    def get_active_dblibrary_instances(baseclass):
        """This is special keyword to get database library instances which are
        inherited from the same base class.
        With this keyword it's possible to find which instance has been "connected"
        and this instance connection can then be shared.
        """
        criteria = lambda x: issubclass(x.__class__, baseclass)
        libraryInstanceList = RobotHelper._get_lib_from_robot_with_criteria(criteria)
        return [lib for lib in libraryInstanceList if lib.connected]

    @staticmethod
    def parse_kwargs_from_positional_args(*args):
        """This keyword will parse keyword type of arguments from the normal
        positional arguments and returns a dictionary from parsed arguments.
        If any of the given positional arguments does not contain "=" char,
        keyword will raise an exception. Also key (left side of the =) must be
        non-empty, otherwice exception is raised.

        This is workaround for the fact that Robot Framework does not support
        keyword arguments like Python supports.

        User should give unlimited number of positional arguments in the form of:
        | ${mydict}= | Parse Kw Args From Positional Args | myFirstKey=value1 | mySecondKey=2nd value |
        ==> mydict now contains {'myFirstKey': 'value1', 'mySecondKey': '2nd value'}

        This keyword is handy to use inside Python keywords to parse keyword arguments
        which are wanted to be given just like keyword arguments in Python.
        There's not much point to use this keyword from Robot testsuite.

        """
        kwargs = OrderedDict()
        for arg in args:
            if arg.find("=") == -1:
                raise ValueError("Invalid usage of keyword type of arguments: '%s'. Character '=' is missing between key and value." % (arg))
            key_and_value = arg.split('=', 1)

            # Check that key cannot be empty
            if key_and_value[0] == '':
                raise ValueError("Invalid usage of keyword type of arguments: '%s'. Key is empty!" % (arg))

            # Store to dict
            kwargs[key_and_value[0]] = key_and_value[1]

        return kwargs

    @staticmethod
    def check_dict_keys(dict_to_check,
                        allowed_values_array,
                        error_msg='Some of the dictionary keys not found from the given allowed values. ',
                        raise_exception=True):
        """This keyword will check that given dictionary key values are all found
        from the given value array.

        Raises an exception if any of the keys are not valid with given `error_msg`
        and with failed keys appended.
        Optionally (`raise_exception` is False), keyword will return array containing
        all erroneous keys or empty array if all are ok.

        """
        erroneus_keys = []
        for key in dict_to_check.iterkeys():
            if key not in allowed_values_array:
                erroneus_keys.append(key)

        if erroneus_keys:
            if raise_exception:
                raise ValueError(error_msg + " Erroneus keys: '%s' not found in allowed values: '%s'" % (', '.join(erroneus_keys), ', '.join(allowed_values_array)))
        return erroneus_keys

    @staticmethod
    def uniquify_list(seq):
        """This keyword returns a uniquified version of the list given as an argument
        Ex. A=[1,2,2,3,4,5,1] , A=uniquify_list(A) -> A=[1,2,3,4,5]
        """
        set1 = set(seq)
        return list(set1)
