import logging
import re


def __set_ne_name(ne_type, dn):
    dns = dn.strip().split("/")
    parttern_ne = r''+ ne_type + "-[^\`\'\"%/]+/"''
    is_ne_type_correct = re.search(parttern_ne, dns[1]+ "/")
    if not is_ne_type_correct:
        logging.error(dns[1] + " format is not correct. It must be " + ne_type + "-<instance>")
        exit(1)
    ne_name = dns[1]
    return ne_name


def process_ne_presentation_name(param_list):
    if not param_list.has_key("NE presentation name"):
        logging.info("NE presentation name is the mandatory parameter, fetch it through DN and NE_TYPE")
        param_list["NE presentation name"] = __set_ne_name(param_list['ne_type'], param_list["DN"])


def exist_null_params(param_list):
    if not param_list.has_key("ne_type"):
        logging.error("ne_type is the mandatory parameter, it can't be null.")
        return False
    if not param_list.has_key("ne_version"):
        logging.error("ne_version is the mandatory parameter, it can't be null.")
        return False
    if not param_list.has_key("DN"):
        logging.error("DN is the mandatory parameter, it can't be null.")
        return False
    if not param_list.has_key("NETACT_HOST"):
        logging.error("NETACT_HOST is the mandatory parameter, it can't be null.")
        return False
    if not param_list.has_key("NETACT_LBWAS"):
        logging.error("NETACT_LBWAS is the mandatory parameter, it can't be null.")
        return False
    return True


def process_credentials(param_list):
    if not param_list.has_key("credentials"):
        logging.info("credentials is the mandatory parameter, Set it as None")
        param_list["credentials"] = None


def verify_mr_format(param_list):
    if not param_list.has_key("MR"):
        logging.error("MR is the mandatory parameter, it can't be null.")
        return False
    else:
        pattern = r'(MRC-[^\`\'\"%/]+/MR-[^\`\'\"%/]+)'
        is_mr_type_correct = re.search(pattern, param_list['MR'])
        if not is_mr_type_correct:
            logging.error("MR must match 'MRC-<instance>/MR-<instance>'")
            logging.error("MR instance cannot contain any of the following characters: " + "`"+ "'" + '"' + "%/")
            return False
    return True


def verify_dn_format(param_list):
    if not param_list.has_key("DN"):
        logging.error("DN is the mandatory parameter, it can't be null.")
        return False
    else:
        pattern = r''"PLMN-[^\`\'\"%/]+/" + param_list['ne_type'] + "-[^\`\'\"%/]+/"''
        is_dn_correct = re.search(pattern, param_list['DN'] + "/")
        if not is_dn_correct:
            logging.error(param_list['DN'] + " format is not correct. It must be PLMN-<instance>/" + param_list['ne_type'] + "-<instance>")
            return False
    return True

