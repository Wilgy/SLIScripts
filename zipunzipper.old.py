"""
zipunzipper.old.py - Given a zip directory of student submissions pulled in
    bulk from myCourses, unzips them and puts them in directories with the
    students' last names.

    NOTE: Since myCourses has changed how they package submissions, this is 
    no longer usable
Author: T. Wilgenbusch
"""

#!/usr/bin/env python

import sys
import os.path

from subprocess import call, check_output
from os import listdir

#place to write all output we don't want to see
devnull = open(os.devnull, 'w')

def main():
    """
    unzips a zip file that contains zip files from dropbox and puts them 
    in the correct student directory
    first argument is the zip file
    second argument is a list of the students (directories) names
    third argument is the Lab directory
    """

    #need to have at least to params
    if(len(sys.argv) <= 2):
        usage()
        exit(1)

    zip_file_name = sys.argv[1]
    student_name_file = ""
    dir_name = ""

    #user included a student file
    if(len(sys.argv) == 4):
        student_name_file = sys.argv[2]
        dir_name = sys.argv[3]

    #user wants to pull the student names from zip files
    elif(len(sys.argv) == 3):
        dir_name = sys.argv[2]

    #incorrect number of arguments
    else:
        usage()
        exit(1)

    if( not os.path.isfile(zip_file_name) or not zip_file_name.endswith('.zip') ):
        print('Zip file does not exist or is not a zip file')
        return

    if( student_name_file != "" and not os.path.isfile(student_name_file) ):
        print('Student file does not exist')
        return

    if(not os.path.exists(dir_name)):
        print('Lab directory does not exist')
        return

    temp_zip_directory_name = "temp_zip_directory"
    if(dir_name.endswith('/')):
        temp_zip_directory_name = dir_name + temp_zip_directory_name
    else:
        temp_zip_directory_name = dir_name + '/' + temp_zip_directory_name
        dir_name = dir_name + '/'

    call(["mkdir", temp_zip_directory_name], stdout=devnull, stderr=devnull)
    call(["unzip", "-d", temp_zip_directory_name, zip_file_name], stdout=devnull, stderr=devnull)
    # find . -type f ! -name "*.*" -delete
    #remove all files that do not have a zip extension
    call(["find", temp_zip_directory_name, "-type", "f", "!", "-name", "*.zip", "-delete"], stdout=devnull, stderr=devnull)

    #grab all of the zip files that were unzipped from dropbox super zip
    output = listdir(temp_zip_directory_name)
    #create the student dictionary 
    student_dict = get_student_dict(student_name_file, output)
    #populate dictionary to pair student names with their correct labs/projects
    #could be optimized? eh whatever
    for student in student_dict.keys():
        for file in output:
            if student in file:
                student_dict[student] += [file]

    #create student directories
    create_dirs_is_nonexistent(student_dict, dir_name)

    #create the student lab directories (could be more)
    unzip_labs(student_dict, dir_name, temp_zip_directory_name)

    #remove the temp directory
    call(["rm", "-r", temp_zip_directory_name], stdout=devnull, stderr=devnull)


def get_student_dict(student_name_file, zip_names):
    """
    given a file containing a list of students, opens them and 
    creates a dictionary with all of the names in them.  If no student file is 
    given, the student dictionary is made from the names in the temp directory
    @param student_name_file the file with the student names
    @param zip_names the list of zip file names in the temp directory
    """
    dict = {}
    if(student_name_file != ''):

        for line in open(student_name_file):
            dict[line.strip()] = []

        # close(student_name_file)
    else:
        for name in zip_names:
            full_name = name.split(" - ")[1]
            last_name = full_name.split(', ')[0]
            if(last_name not in dict.keys()):
                dict[last_name.strip()] = []

    return dict



def create_dirs_is_nonexistent(student_dict, root_dir):
    """
    creates the student directory structure based on the student names passed 
    in if it doesn't already exist
    @param student_dict the dictionary that contains all the student names
    @param root_dir the parent directory to put all of the student directories
    """
    if(not root_dir.endswith('/')):
        root_dir += '/'
    for student in student_dict.keys():
        if(not os.path.exists(root_dir + student)):
            call(["mkdir", root_dir + student], stdout=devnull, stderr=devnull)

def unzip_labs(student_dict, dir_name, temp_zip_directory_name):
    """
    unzips all of the lab zip files and places them in the correct directories
    will warn the user if it was unable to get certain labs for certain files
    @param student_dict the dictionary of students
    @param dir_name the directory to unzip all of the labs into
    @param temp_zip_directory_name name of directory with temp labs
    """
    for student in student_dict.keys():
        for file in student_dict[student]:
            #if there are more than one labs submitted, we want to save the in seperate directories
            if(len(student_dict[student]) > 1):
                first_split = file.split(" - ")
                if(len(first_split)  > 2):
                    file_directory_name = first_split[2]
                    second_split = file_directory_name.split(".zip")
                    if(len(second_split) > 0):
                        file_directory_name = second_split[0]
                        call(["mkdir", dir_name + student + '/' + file_directory_name], stdout=devnull, stderr=devnull)
                        call(["unzip", "-d", dir_name + student +  '/' + file_directory_name, temp_zip_directory_name + '/' + file], stdout=devnull, stderr=devnull)
                    else:
                        print("ERROR: Unable to unzip lab: " + file + "for student: " + student)
                else:
                    print("ERROR: Unable to unzip lab: " + file + "for student: " + student)
            #otherwise they only have one lab submitted and we should just unzip it here
            else:
                call(["unzip", "-d", dir_name + student, temp_zip_directory_name + '/' + file], stdout=devnull, stderr=devnull)
        
        if(len(student_dict[student]) == 0):
            print("WARNING: Could not find labs for student: " + student)

def usage():
    """
    prints the usage statement for the script
    """
    print('usage: python zipunzipper.py zipfile [students] dirname')
    print('     zipfile  - The zip file downloaded from myCourses that contains all the labs')
    print('     students - file containing all the students name (new line delimited). If not')
    print('            provided, the names will be pulled from the lab files.')
    print('     dirname  - the name of the directory to drop all of the labs (i.e ./course/labs/lab01/')

main()