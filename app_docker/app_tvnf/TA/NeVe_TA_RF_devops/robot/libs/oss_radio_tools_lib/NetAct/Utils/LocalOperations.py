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


import robot.libraries.OperatingSystem
import shutil
import zipfile
import tarfile
import os.path
import platform


__version__ = '0.1.0'


class LocalOperations(object):
    '''
    This library is for doing general local operations. for create dir and such operations, use OS library.
    
    Refactoring was made by Saku Rautiainen, most of the functionality was originally done by Timo Kivipelto
    Author: saku.rautiainen@nsn.com and timo.kivipelto@nsn.com
    '''

    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'
    ROBOT_LIBRARY_VERSION = __version__
    
    def __init__(self):
        self.op = robot.libraries.OperatingSystem.OperatingSystem()
        
    def empty_dir(self, dirname):
        """Empties given directory
        @var dirname: directory name
        
        Example:
        | Empty Dir | ${dir}  |
        """
        filelist = self.return_file_list(dirname, "all")
        print "*DEBUG* removing files form dir " + dirname + " : " + str(filelist)
        for afile in filelist:
            os.remove(dirname + "/" + afile)
    
    def return_file_list(self, dirname, str_suffix):
        """Lists files in certain directory with certain type. 
        This function is meant to be run in local machine.
        @var dirname: name of the directory
        @var str_suffix: file's suffix. Example "xml". IF "all" THEN EVERY FILE WILL BE LISTED 
        @return: List of files in directory
        @raise OSError: directory not found
        
        Example:
            | Return file List | $dirname | ".html" |
        """
        try:
            dirList = os.listdir(dirname)
            dirList2 = os.listdir(dirname)
            if str_suffix != "all":
                for fname in dirList:
                    suffix = fname.split(".")
                    size = len(suffix)
                    if suffix[size - 1] != str_suffix:
                        dirList2.remove(fname)
            else:
                dirList2 = os.listdir(dirname)
            return dirList2
        except OSError:
            print "Couldn't open directory " + dirname
            
    def return_file_list_with_path(self, dirname, str_suffix):
        """Lists files in certain directory with certain type. 
        This function is meant to be run in local machine.
        @var dirname: name of the directory
        @var str_suffix: file's suffix. Example "xml". IF "all" THEN EVERY FILE WILL BE LISTED 
        @return: List of files in directory WITH PATHNAME
        @raise OSError: directory not found
        
        Example:
            | Return File list With Path | $dirname | ".html" |
        """
        filelist = self.return_file_list(dirname, str_suffix)
        newfilelist = []
        for afile in filelist:
            newfilelist.append(dirname + os.sep + afile)
        return newfilelist
    
    def ReplaceInFile(self, filename, pattern, value, replace_all="yes", new_file=""):
        """This keyword implements Find and Replace functionality for given file. 
        If given pattern is found, it is replaced with given value. 
        replace_all and new_file parameter are optional parameters.
        If replace_all is not "yes" then only one pattern (first occurrence) is replaced.
        If new_file is filled, new modified file is created and original file
        stays untouched. Search method is case sensitive. 
        Absolute paths must be used for filenames.
        Author: Timo Kivipelto
        """
        found = "false"   
        input_file = open(filename, "r")
        output = open("output_temp_file", "w")        
        for line in input_file.readlines():
            if line.find(pattern) != -1:  # Does not match pattern                                  
                # This line should be replaced. 
                # We have to check can this still be replaced
                if found == "false" or replace_all == "yes":
                    found = "true"
                    if replace_all == "yes":
                        line = line.replace(pattern, str(value))  # replace all occurrences from line                        
                    else:
                        line = line.replace(pattern, str(value), 1)  # replace only first occurrence from line
                        
            output.write(line)     
        input_file.close()
        output.close()
        if len(new_file) == 0:
            shutil.move("output_temp_file", filename)
        else:
            shutil.move("output_temp_file", new_file)
             
    def remove_lines_in_file(self, filename, pattern, new_file=""):
        """This keyword implements Find and Remove Line functionality for given file. 
        If given pattern is found from line, that line it removed. 
        new_file parameter is optional.
        If new_file is filled, new modified file is created and original file
        stays untouched. Search method is case sensitive. 
        Absolute paths must be used for filenames.
            
        Example:
                | Remove Lines In File | $dirname | ".html" |
        """    
        input_file = open(filename, "r")
        output = open("output_temp_file", "w")        
        for line in input_file.readlines():
            if line.find(pattern) != -1:  # find line that will be removed
                continue                                    
            output.write(line)
        input_file.close()
        output.close()
        if len(new_file) == 0:
            shutil.move("output_temp_file", filename)
        else:
            shutil.move("output_temp_file", new_file)

    def number_of_patterns_in_file(self, filename, pattern):   
        """This keyword counts how many times given 
        search pattern exists in given file.
        Search method is case sensitive. 
        Absolute paths must be used for filename.
            
        Example:
        | Number Of Patterns In File | $filename | "ADAPTATION_ID" |
        """
        i = 0
        input_file = open(filename, "r")    
        for line in input_file.readlines():
            while line.find(pattern) != -1:  # find text from line
                line = line.replace(pattern, "", 1)  # replace text with replacement                                                    
                i = i + 1
        return i

    def number_of_lines_in_file(self, filename):   
        """This keyword returns line numbers of given file. 
        Absolute paths must be used for filename.
            
        Example:
        | Number Of Lines In File | $filename |
        """
        i = 0
        input_file = open(filename, "r")
        for _line in input_file.readlines():
            i = i + 1
        input_file.close()
        return i
        
    def modify_file_list_with_suffix(self, filelist, suffix):
        """Modifies given filelist with given suffix
        @return: list of filenames with suffix
            
        Example:
        | Modify Files List With Suffix | @filelist| ".xml" |
        """
        newlist = []
        for afile in filelist:
            newlist.append(str(afile + suffix))
        return newlist                 

    @staticmethod
    def is_file_archived(archive):
        """Checks whether file is archived or not.
        @param file: Either file-like object or name of the name (with absolute file path)
        @return: True when file is of known archive, otherwise False 
        @author: petri.saarelainen.ext@nsn.com
        """
        if zipfile.is_zipfile(archive):  # check whether file is zipped file
            return True
        elif tarfile.is_tarfile(archive):
            return True
        else:
            return False

    @staticmethod        
    def get_file_objects_from_archive_for_reading(archive):
        """Returns list of file-like objects inside archived file.
        The file-like object is read-only and provides the following methods: read(), readline(), readlines(), __iter__(), next()
        Also it is possible to pass this file-like object to for example XML parser.
        
        Currently supports zip and tar (also compressed) archives.
        Note! file-like objects should be closed after usage.
        
        @param archive: Either file-like object or name of the name (with absolute file path)
        @return: List of file-like objects from within archive
        @author: petri.saarelainen.ext@nsn.com
        """
        fileObjectList = []
        if zipfile.is_zipfile(archive):  # check whether file is zipped file
            #print "*DEBUG*ZipFile found:",str(archive).lower()
            zf = zipfile.ZipFile(archive, 'r')
            for fileInZip in zf.infolist():
                print "*DEBUG*File found from Zip:", str(fileInZip.filename)
                zfo = zf.open(fileInZip, 'rU')
                fileObjectList.append(zfo)
            zf.close()  # can be closed here already
        elif tarfile.is_tarfile(archive):
            #print "*DEBUG*Tar File found:",str(archive).lower()
            tf = tarfile.open(archive, 'r:*')  # try open tar with all possible compression methods.
            for memberInfo in tf.getmembers():
                print "*DEBUG*File found from Tar:", str(memberInfo.name)
                tfo = tf.extractfile(memberInfo)
                fileObjectList.append(tfo)
            
            # Note! tar archives can't be closed until handling of file objects from inside archive has finished.
            # zip archives can be closed right after file object is opened.            
        else:
            raise RuntimeError("File is not archive of known type or not an archive at all.")
        
        return fileObjectList

    @staticmethod
    def return_file_list_from_archive(archive):
        """Returns list of filenames from archive.
        @param archive: File-like object of absolute path to archive file.
        @return: List of filenames
        @author: petri.saarelainen.ext@nsn.com
        """
        filelist = []
        if zipfile.is_zipfile(archive):
            zf = zipfile.ZipFile(archive, 'r')
            for fileInZip in zf.namelist():
                filelist.append(str(fileInZip))
            zf.close()
        elif tarfile.is_tarfile(archive):
            tf = tarfile.open(archive, 'r:*')
            for fit in tf.getnames():
                filelist.append(str(fit))
            tf.close()
        return filelist

    @staticmethod
    def extract_files_from_archive(archive, filesToBeExtracted, destination):
        """Extracts file from archive to destination folder.
        @author: petri.saarelainen.ext@nsn.com
        @param archive: absolute path name to archive or file like archive object.
        @param destination: destination folder path
        @param filesToBeExtracted: List of Files to be extracted from archive
        @return: list of extracted files
        """
        extracted = []
        if os.path.exists(archive) and os.path.isfile(archive):
            if os.path.exists(destination) and os.path.isdir(destination):
                if zipfile.is_zipfile(archive):
                    zf = zipfile.ZipFile(archive, 'r')
                    for fileToBeExtracted in filesToBeExtracted:
                        if fileToBeExtracted in zf.namelist():
                            zf.extract(fileToBeExtracted, destination)
                            extracted.append(fileToBeExtracted)
                    zf.close()
                elif tarfile.is_tarfile(archive):
                    tf = tarfile.open(archive, 'r:*')
                    for fileToBeExtracted in filesToBeExtracted:
                        if fileToBeExtracted in tf.getnames():
                            tf.extract(fileToBeExtracted, destination)
                            extracted.append(fileToBeExtracted)
                    tf.close()
                else:
                    raise RuntimeError("File %s isn't archive of known type " % archive)
            else:
                raise RuntimeError("Destination %s not found or isn't directory" % destination)
        else:
            raise RuntimeError("File %s doesn't exist " % archive)        
        return extracted
    
    def create_http_link_to_local_file(self, local_file, offset="", cutOff=""):
        """This keyword creates link to existing local file. 
        file must be given by using absolute path.
        From the given path everything before cutOff is replaced with offset string.
        Example: file is "/var/opt/nokia/error.log" offset = "/tmp" cutOff = "opt"
        Keyword will create link that points to "/tmp/opt/nokia/error.log"
        """
        basename = os.path.basename(local_file)        
        path = os.path.dirname(local_file)
        if offset != "":
            if path.find(cutOff) != -1:
                systemPath = os.path.dirname(local_file)
                before, sep, after = systemPath.partition("/")
                while True:
                    if before == cutOff:
                        path = offset + sep + before + sep + after
                        break
                    before, sep, after = after.partition("/")
        
        if platform.system() == 'Linux':
            host = os.popen('hostname -f').read()
            httpPath = "http://" + host + "/" + path + "/" + basename
        else:
            httpPath = "file:///" + path + "/" + basename        
        print "*HTML* <b>Link to file:</b>  <a href=\"" + httpPath + "\">" + basename + "</a>"    
