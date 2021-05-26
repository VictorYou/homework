# __author__ = 'x5luo'
import os
import re
from time import sleep

import datetime
import paramiko
import logging
import LocalFileOperations


class RemoteOperations(object):
    def __init__(self):
        self.ssh_client = paramiko.SSHClient()
        self.local_file_operations = LocalFileOperations.LocalFileOperations()

    def open_conn_and_login(self, host, username, password, port=22):
        logging.info("Login " + host + " Username: " + username + " start.")
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(hostname=host, username=username, password=password, port=port, timeout=20)
        logging.info("Login " + host + " Username: " + username + " done.")

    def close_conn(self):
        logging.info("Close the remote connection start.")
        self.ssh_client.close()
        logging.info("Close the remote connection done.")

    def display_error_list_information(self, errors):
        for error in errors:
            logging.error(error)

    def display_list_information(self, messages):
        for information in messages:
            logging.info(information)

    def execute_command(self, command, input_value=""):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        # stdin, stdout, stderr = self.ssh_client.exec_command("echo &?")
        if not input_value == "":
            stdin.write(input_value)
            stdin.flush()
        errors = stderr.readlines()
        if len(errors) > 0:
            logging.error(len(errors))
            logging.error("Execute command %s failed.\nReason:", command)
            self.display_error_list_information(errors)
            # raise RuntimeError("Execute command " + command + " failed.")
        return stdout.readlines()

    def execute_command_ignore_error(self, command, input_value=""):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        if not input_value == "":
            stdin.write(input_value)
            stdin.flush()
        return stdout.readlines(), stderr.readlines()

    def execute_command_with_str_response(self, command):
        result = self.execute_command(command)
        return "".join(result)

    def execute_command_with_immediately_output(self, command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        # while True:
        #     next_line = stdout.readline()
        #     if next_line == "":
        #         break
        #     logging.info(next_line)
        output = {}
        output["stdout"] = stdout
        output["stderr"] = stderr
        return output

    def execute_command_with_ingore_response(self, command):
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return

    def __get_root_permission(self, channel, root_password):
        channel.send('su - \n')
        buffer = ''
        while not buffer.endswith('Password: '):
            buffer = channel.recv(1024)
        channel.send(root_password + '\n')
        buffer = ''
        while not buffer.endswith('# '):
            if buffer.strip().find('incorrect password') != int(-1):
                channel.close()
                raise AssertionError("Wrong root password")
            buffer += channel.recv(1024)

    def __parser_output_content_for_root_command(self, content):
        lines = content.split('\n')
        output = ''
        if len(lines) <= int(2):
            return output
        for i in range(len(lines) - 2):
            output += lines[i + 1].strip() + "\n"
        return output

    def __receive_output_for_root_command(self, channel, end_flag):
        buffer = ''
        while not buffer.endswith(end_flag):
            buffer += channel.recv(1024)
        buffer, number = re.subn('\n\\' + end_flag + '$', end_flag, buffer)
        return buffer

    def __check_root_permission(self, channel):
        channel.send('whoami \n')
        buffer = ''
        sleep(1)
        while not buffer.endswith('$ ') and not buffer.endswith('# '):
            buffer += channel.recv(1024)
        if buffer.find('root') != -1:
            return True
        return False

    def execute_command_with_root(self, command, root_password, error_raise=True):
        chan = self.ssh_client.invoke_shell()
        if not self.__check_root_permission(chan):
            self.__get_root_permission(chan, root_password)
        command.strip(' ')
        if command.startswith("ls"):
            chan.send(command + ' --color=never\n')
        else:
            chan.send(command + '\n')
        result = self.__parser_output_content_for_root_command(self.__receive_output_for_root_command(chan, '# '))
        chan.send("echo $? \n")
        error_code = self.__parser_output_content_for_root_command(self.__receive_output_for_root_command(chan, '# '))
        if error_raise and int(error_code) != 0:
            chan.close()
            raise AssertionError("Execute command " + command + " Failed: " + result)
        chan.close()
        return re.split('[\n]', result)

    def check_file_exist(self, file_path):
        stdin, stdout, stderr = self.ssh_client.exec_command("ls " + file_path)
        if len(stderr.readlines()) > 0:
            return False
        return True

    def check_directory_exist(self, directory_path):
        stdin, stdout, stderr = self.ssh_client.exec_command('[ -d ' + directory_path + ' ] && echo "exists"')
        result = stdout.readlines()
        if len(result) > int(0) and str(result[0]).strip() == 'exists':
            return True
        return False

    def create_remote_directory(self, directory_file_path, user, group, mod='755'):
        if self.check_directory_exist(directory_file_path):
            logging.info("The directory " + directory_file_path + " is already exist")
        else:
            command = 'mkdir -p ' + directory_file_path + ' && ' + 'chown ' + user + ':' + group + ' ' \
                      + directory_file_path + ' && ' 'chmod ' + mod + ' ' + directory_file_path
            logging.info("The command is " + command)
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

    def get_file_content(self, file_path):
        if not self.check_file_exist(file_path):
            raise AssertionError("File is not exist: " + file_path)
        else:
            result = self.execute_command_with_str_response("cat " + file_path)
        return result

    def upload_file_to_remote(self, target_host, username, password, src_path, target_path, port=22):
        transport = paramiko.Transport((target_host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(src_path, target_path)
        sftp.close()

    def __upload_directory_to_remote(self, local_dir, remote_dir, sftp):
        if not remote_dir.endswith("/"):
            remote_dir += "/"
        try:
            sftp.mkdir(remote_dir)
        except Exception:
            pass
        for root, dirs, files in os.walk(local_dir):
            for filepath in files:
                local_file = os.path.join(root, filepath)
                remote_file = remote_dir + filepath
                sftp.put(local_file, remote_file)
            for name in dirs:
                local_path = os.path.join(root, name)
                remote_path = remote_dir + name
                self.__upload_directory_to_remote(local_path, remote_path, sftp)

    def upload_directory_to_remote(self, target_host, username, password, local_dir, remote_dir, port=22):
        if not remote_dir.endswith("/"):
            remote_dir += "/"
        try:
            t = paramiko.Transport((target_host, port))
            t.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(t)
            logging.info('upload file start ' + str(datetime.datetime.now()))
            self.__upload_directory_to_remote(local_dir, remote_dir, sftp)
            logging.info('upload file success ' + str(datetime.datetime.now()))
            t.close()
        except Exception, e:
            print e

    def download_file_to_local(self, target_host, username, password, remote_path, local_directory_path,
                               local_filename=None):
        if not self.local_file_operations.check_directory_exist(local_directory_path):
            self.local_file_operations.create_directory(local_directory_path)
        if not str(local_directory_path).endswith("/"):
            local_directory_path += "/"
        if local_filename is None:
            local_filename = str(remote_path).rsplit("/", 1)[1]
        transport = paramiko.Transport((target_host, 22))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_path, local_directory_path + local_filename, None)
        sftp.close()

    def get_file_list_in_directory(self, directory_path, throw_error=False):
        if not throw_error:
            result, errors = self.execute_command_ignore_error("ls " + directory_path)
        else:
            result = self.execute_command("ls " + directory_path)
        files = []
        for file in result:
            files.append(file.strip('\n\r'))
        return files
