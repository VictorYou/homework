

import pexpect
from Utils.Logger import LOGGER


class ExpectSession(object):

    def __init__(self):
        pass

    def get_root_session(self, host, omc_user, omc_password, root_password):
        expect_process = self.get_omc_session(host, omc_user, omc_password)
        expect_process.sendline("su -")
        ret_code = expect_process.expect(["Password:", pexpect.EOF, pexpect.TIMEOUT])
        if ret_code == 0:
            expect_process.sendline(root_password)
            ret_code = expect_process.expect(["(?i)incorrect password(?i)", "(i?)]#", pexpect.TIMEOUT])
            if ret_code == 0:
                LOGGER.warn("Wrong root password")
                raise AssertionError("Wrong root password")
            elif ret_code == 2:
                LOGGER.warn("Time out for session")
                raise AssertionError("Time out for session")
        return expect_process

    def get_omc_session(self, host, omc_user, omc_password):
        cmd = 'ssh ' + omc_user + '@' + host
        LOGGER.info(cmd)
        expect_process = pexpect.spawn(cmd)
        ret_code = expect_process.expect(
                ["(?i)continue connecting (yes/no)?", "(?i)password:", pexpect.EOF, pexpect.TIMEOUT])
        if ret_code == 0:
            expect_process.sendline("yes")
            ret_code = expect_process.expect(["(?i)password:", pexpect.EOF, pexpect.TIMEOUT])
            if ret_code == 0:
                expect_process.sendline(omc_password)
                ret_code = expect_process.expect(["(?i)password:", pexpect.EOF, pexpect.TIMEOUT])
                if ret_code == 0:
                    LOGGER.warn("Wrong password for %s" % omc_user)
                    raise AssertionError("Wrong password for %s" % omc_user)
            else:
                LOGGER.warn("Login to %s error" % host)
                raise AssertionError("Login to %s error" % host)
        elif ret_code == 1:
            expect_process.sendline(omc_password)
            ret_code = expect_process.expect(["(?i)password:", "(i?)~](?i)", pexpect.TIMEOUT])
            if ret_code == 0:
                LOGGER.warn("Wrong password for user %s" % omc_user)
                raise AssertionError("Wrong password for user %s" % omc_user)
            elif ret_code == 2:
                LOGGER.warn("Time out for SSH login")
                raise AssertionError("Time out for SSH login")
        return expect_process