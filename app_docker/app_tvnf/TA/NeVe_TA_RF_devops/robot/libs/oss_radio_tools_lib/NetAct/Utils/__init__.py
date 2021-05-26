from DnUtils import DnUtils
from LocalOperations import LocalOperations
from VariablesHelper import VariablesHelper
from WebServiceChecking import *
from PathHandler import PathHandler

def wrap_as_list(param):
    return list(param) if isinstance(param, (list,tuple)) else [param]
def insert_prefix_at_head_per_line(content,prefix,insertion_num=1):
    return reduce(lambda x,y:u"%s%s%s\n"%(x,prefix*insertion_num,y),content.splitlines(),u"")
def insert_tab_at_head_per_line(content,tab_num=1):
    return insert_prefix_at_head_per_line(content, "\t", tab_num)
