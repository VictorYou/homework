import os
import sys
import shutil

__author__ = 'x5luo'


class LocalFileOperations(object):
    def __init__(self):
        pass

    def create_directory(self, directory_path):
        os.mkdir(directory_path)

    def delete_directory(self, directory_path):
        if self.check_directory_exist(directory_path):
            shutil.rmtree(directory_path)

    def delete_file(self, file_path):
        if self.check_file_exist(file_path):
            os.remove(file_path)

    def check_directory_exist(self, directory_path):
        return os.path.exists(directory_path)

    def check_file_exist(self, file_path):
        return os.path.exists(file_path)

    def write_content_to_file(self, file_full_path, content):
        file = open(file_full_path, "w")
        file.write(content)
        file.close()

    def get_current_directory(self):
        current_directory = sys.argv[0].rsplit('/', 1)
        return current_directory[0]

    def get_files_name_in_directory(self, directory_path):
        if not os.path.exists(directory_path):
            raise AssertionError("The path %s not exist.", directory_path)
        if not os.path.isdir(directory_path):
            raise AssertionError("The path %s is not a directory.", directory_path)
        return os.listdir(directory_path)

    def get_file_content(self, file_path):
        if not os.path.exists(file_path):
            raise AssertionError("The file %s not exist.", file_path)
        if not os.path.isfile(file_path):
            raise AssertionError("The %s is not a file.", file_path)
        return open(file_path).readlines()
