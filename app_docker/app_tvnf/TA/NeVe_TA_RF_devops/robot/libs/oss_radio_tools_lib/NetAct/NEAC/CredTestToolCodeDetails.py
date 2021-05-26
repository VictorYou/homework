# __author__ = 'x5luo'
class CredTestToolCodeDetails(object):
    errors = {0: "OK", 1: "Status UNKNOWN",
              2: "Status ACTIVATION ONGOING",
              3: "Status ACTIVATION OK",
              4: "Status ACTIVATION FAILED",
              5: "Status DEACTIVATION ONGOING",
              6: "Status DEACTIVATION OK",
              7: "Status DEACTIVATION FAILED",
              8: "Status PASSWORD UPDATE ONGOING",
              9: "Status PASSWORD UPDATE OK",
              10: "Status PASSWORD UPDATE FAILED",
              11: "Status NEW",
              12: "Status NO LICENSE",
              20: "Status NEAC ACCOUNT PROVISION STARTED",
              21: "Status NEAC ACCOUNT PROVISION COMPLETED",
              22: "Status NEAC ACCOUNT PROVISION PARTLY",
              23: "Status NEAC ACCOUNT PROVISION FAILED",
              24: "Status NEAC ACCOUNT PROVISION NEW",
              25: "Status NEAC ACCOUNT PROVISION MODIFIED",
              26: "Status NEAC ACCOUNT PROVISION DELETED",
              50: "Error GENERIC EXCEPTION",
              51: "Error ILLEGAL ARGUMENT EXCEPTION",
              52: "Error CNUM MANAGEMENT ACCESS EXCEPTION",
              71: "Error NETWORK ELEMENT DOES NOT EXIST",
              91: "Error ACTION NOT SUPPORTED",
              103: "Error CREDENTIAL PROVISIONING FAILED",
              101: "Error CREDENTIAL CREATION FAILED",
              102: "Error CREDENTIAL DELETION FAILED"
              }

    def __init__(self):
        pass

    def get_errors_code_details(self, error_code):
        return self.errors[error_code]
