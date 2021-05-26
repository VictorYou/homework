#  Copyright 2010-2012 Nokia Siemens Networks Oyj
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

from copy import deepcopy

__version__ = '0.1'


class DnUtils(object):
    """DnUtils is a test library for Robot Framework which enables
    different operations for DN (Distinguished Name).

    DnUtils can be used from any other python library or imported to Robot html testsuite.

    Author: samuli.silvius@nsn.com
    """

    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'
    ROBOT_LIBRARY_VERSION = __version__

    TRIVIAL = 'trivial'
    OVERLAP = 'overlap'
    PREPEND = 'prepend'
    
    @classmethod
    def get_relative_dn(cls, dn):
        """Returns last relative distinguished name (RDN) of given DN.

        Examples:
        | ${rnd}= | Get Relative Dn | PLMN-PLMN/NTHLRFE-99/PLATFORM-22/CFRAME-33 |
        ==> Returns CFRAME-33
        """
        objects = dn.rsplit("/", 1)
        if len(objects) == 1:
            last_object = objects[0]
        else:
            last_object = objects[1]

        if last_object == "":
            raise AssertionError("DN '%s' not valid" % dn)
        return last_object

    @classmethod
    def get_object_instance(cls, dn):
        """Returns object instance of given DN.

        Examples:
        | ${instance}= | Get Object Instance | PLMN-PLMN/NTHLRFE-99/PLATFORM-22/CFRAME-33 |
        ==> Returns 33
        """
        last_object = cls.get_relative_dn(dn)
        return cls._get_class_and_instance_from_dn(last_object)[1]

    @classmethod
    def get_object_class(cls, dn):
        """Returns object class abbreviation of the given DN.

        Examples:
        | ${object_class}= | Get Object Class | PLMN-PLMN/NTHLRFE-99/PLATFORM-22/CFRAME-33 |
        ==> Returns CFRAME
        """
        last_object = cls.get_relative_dn(dn)
        return cls._get_class_and_instance_from_dn(last_object)[0]

    @classmethod
    def _get_class_and_instance_from_dn(cls, dn):
        object_split = dn.rsplit("-", 1)
        if len(object_split) != 2 or object_split[0] == "" or object_split[1] == "":
            raise AssertionError("DN '%s' not valid" % dn)
        return object_split

    @classmethod
    def get_parent_dn(cls, dn):
        """Returns parent dn of given dn.
        If dn does not have parent (root itself) returns None.

        Examples:
        | ${parent}= | Get Parent Dn | PLMN-PLMN/NTHLRFE-99/PLATFORM-22/CFRAME-33 |
        ==> Returns PLMN-PLMN/NTHLRFE-99/PLATFORM-22
        """
        last_object = cls.get_relative_dn(dn)
        objects = dn.rsplit(last_object, 1)
        if objects[0] == "":
            return None
        return objects[0].rstrip("/")

    @classmethod
    def get_root_dn(cls, dn):
        """Returns root object of given DN.

        Examples:
        | ${root}= | Get Root Dn | PLMN-PLMN/NTHLRFE-99/PLATFORM-22/CFRAME-33 |
        ==> Returns PLMN-PLMN
        | ${root}= | Get Root Dn | PLMN-PLMN |
        ==> Returns PLMN-PLMN
        """
        return dn.split("/", 1)[0]

    @classmethod
    def is_root(cls, dn):
        """Returns True is given DN is a root DN. Otherwise False.
        """
        return cls.get_relative_dn(dn) == cls.get_root_dn(dn)

    @classmethod
    def is_descendant(cls, ancestor_dn, dn):
        """Returns True is given dn is descendant of given ancestor dn.

        Examples:
        | ${bool_value}= | Is Descendant | PLMN-PLMN/NTHLRFE-99/PLATFORM-22 | PLMN-PLMN/NTHLRFE-99/PLATFORM-22/CFRAME-33 |
        ==> Returns True
        | ${bool_value}= | Is Descendant | PLMN-PLMN/NTHLRFE-99 | PLMN-PLMN/NTHLRFE-99/PLATFORM-22/CFRAME-33 |
        ==> Returns True
        """
        if len(dn) > len(ancestor_dn):
            if dn.startswith(ancestor_dn) and dn[len(ancestor_dn)] == '/':
                return True
        return False

    @classmethod
    def is_descendant_or_equal(cls, ancestor_dn, dn):
        """Returns True is given dn is descendant or equal of given ancestor dn.

        """
        return (dn == ancestor_dn) or cls.is_descendant(ancestor_dn, dn)

    @classmethod
    def change_dn_for_prepend_strategy(self, agent_fqdn, object_fqdn):
        """Returns a dn which is changed to use PREPEND
        STRATEGY.
        In the PREPEND strategy, object DN must begin with agent class. Given DNs must
        be in FQDN format.
        E.g.
        | ${modified_dn} | Change Dn For Prepend Strategy | PLMN-PLMN/NTHLRFE-2 | PLMN-PLMN/NTHLRFE-2/SMI-1/SYSM-1/SYCONFDACC-1/SSTABLE-147 |
        => Returns SMI-1/SYSM-1/SYCONFDACC-1/SSTABLE-147
        """
        object_hierarchy_under_agent = object_fqdn.split(agent_fqdn)
        if len(object_hierarchy_under_agent) == 1:
            return ''
        return object_hierarchy_under_agent[1]

    @classmethod
    def change_multiple_dns_for_prepend_strategy(self, agent_fqdn, value_list, step=1):
        """Returns a list where DNs are mapped to be used for PREPEND STRATEGY.
        I.e. given `agent_fqdn` is removed from DNs.
        In the PREPEND strategy, object DN must begin with agent class.
        `step` parameter can be given if list is wanted to loop as different
        steps as 1 which is a default meaning that each value from given list is
        mapped.
        E.g.
        | ${modified_dn_list}= | Change Multiple Dns For PREPEND Strategy | PLMN-PLMN/NTHLRFE-2 | [PLMN-PLMN/NTHLRFE-2/SMI-1/SYSM-1/SYCONFDACC-1/SSTABLE-147] |
        => Returns [NTHLRFE-2/SMI-1/SYSM-1/SYCONFDACC-1/SSTABLE-147]

        | ${modified_dn_list}= | Change Multiple Dns For PREPEND Strategy | PLMN-PLMN/NTHLRFE-2 | ["PLMN-PLMN/NTHLRFE-2/SMI-1", "PLMN-PLMN/NTHLRFE-2/SMI-2", "PLMN-PLMN/NTHLRFE-2/SMI-3"] | 3 |
        => Returns ["SMI-1", "PLMN-PLMN/NTHLRFE-2/SMI-2", "PLMN-PLMN/NTHLRFE-2/SMI-3"]
        I.e. in 3 steps.
        """
        return_list = deepcopy(value_list)
        for index in range(0, len(value_list), int(step)):
            return_list[index] = self.change_dn_for_prepend_strategy(agent_fqdn, value_list[index])
        return return_list
        
    @classmethod
    def change_dn_for_overlap_strategy(self, agent_fqdn, object_fqdn):
        """Returns DN which is changed to use OVERLAP STRATEGY.
        In the OVERLAP strategy, object DN must begin with agent class. Given DNs must
        be in FQDN format.
        E.g.
        | ${modified_dn} | Change Dn For Overlap Strategy | PLMN-PLMN/NTHLRFE-2 | PLMN-PLMN/NTHLRFE-2/SMI-1/SYSM-1/SYCONFDACC-1/SSTABLE-147 |
        => Returns NTHLRFE-2/SMI-1/SYSM-1/SYCONFDACC-1/SSTABLE-147
        """
        object_hierarchy_under_agent = object_fqdn.split(agent_fqdn)
        if len(object_hierarchy_under_agent) == 1:
            return object_hierarchy_under_agent[0]
        agent_object = agent_fqdn.rsplit("/", 1)[1]
        return agent_object + object_hierarchy_under_agent[1]

    @classmethod
    def change_multiple_dns_for_overlap_strategy(self, agent_fqdn, value_list, step=1):
        """Returns a list where DNs are mapped to be used for OVERLAP STRATEGY.
        I.e. given `agent_fqdn` is removed from DNs.
        In the OVERLAP strategy, object DN must begin with agent class.
        `step` parameter can be given if list is wanted to loop as different
        steps as 1 which is a default meaning that each value from given list is
        mapped.
        E.g.
        | ${modified_dn_list}= | Change Multiple Dns For Overlap Strategy | PLMN-PLMN/NTHLRFE-2 | [PLMN-PLMN/NTHLRFE-2/SMI-1/SYSM-1/SYCONFDACC-1/SSTABLE-147] |
        => Returns [NTHLRFE-2/SMI-1/SYSM-1/SYCONFDACC-1/SSTABLE-147]

        | ${modified_dn_list}= | Change Multiple Dns For Overlap Strategy | PLMN-PLMN/NTHLRFE-2 | ["PLMN-PLMN/NTHLRFE-2/SMI-1", "PLMN-PLMN/NTHLRFE-2/SMI-2", "PLMN-PLMN/NTHLRFE-2/SMI-3"] | 3 |
        => Returns ["NTHLRFE-2/SMI-1", "PLMN-PLMN/NTHLRFE-2/SMI-2", "NTHLRFE-2/SMI-3"]
        I.e. in 3 steps.
        """
        return_list = deepcopy(value_list)
        for index in range(0, len(value_list), int(step)):
            return_list[index] = self.change_dn_for_overlap_strategy(agent_fqdn, value_list[index])
        return return_list
    
    @classmethod
    def get_dn_after_overlap_strategy(cls, agent_fqdn, object_dn):
        """
        """
        if not agent_fqdn.strip() or not object_dn.strip():
            print "*WARN* Invalid agent FQDN (OMES filename) or object DN (OMES content)."
        last_fqdn_list = []
        agent_fqdn_splitted = agent_fqdn.split('/') if '/' in agent_fqdn else [agent_fqdn]
        object_dn_splitted = object_dn.split('/') if '/' in object_dn else [object_dn]
        index = 0
        for agent_object in agent_fqdn_splitted:
            for content_object in object_dn_splitted[index:]:
                if agent_object.split('-')[0] == content_object.split('-')[0]:
                    index += 1
                last_fqdn_list.append(agent_object)
                break
        if index < len(object_dn_splitted):
            last_fqdn_list.extend(object_dn_splitted[index:])
        return '/'.join(last_fqdn_list)

    @classmethod
    def get_dn_after_prepend_strategy(cls, agent_fqdn, object_dn):
        """
        """
        agent_fqdn_splitted = agent_fqdn.split('/') if '/' in agent_fqdn else [agent_fqdn]
        object_dn_splitted = object_dn.split('/') if '/' in object_dn else [object_dn]
        last_fqdn_list = agent_fqdn_splitted + object_dn_splitted
        return '/'.join(last_fqdn_list)
