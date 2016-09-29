#!/usr/bin/env python

"""
zipunzipper.py - Given a zip directory of student submissions pulled in
    bulk from myCourses, unzips them and puts them in directories with the
    students' user names.

Author: T. Wilgenbusch
"""

import sys
import os.path

from subprocess import call, check_output
from os import listdir

#place to write all output we don't want to see
devnull = open(os.devnull, 'w')

def get_student_dict(student_name_file, file_list, temp_zip_directory_name):
    """
    get_student_dict - given a file containing student usernames and full names, 
        will return a dictionary that maps student user names to file names in 
        list of files

    Final dictionary: (key, value) -> (username, {file1, file2})

    @param student_name_file the file with the student names
    @param file_list the list of zip file names in the temp directory
    """

    # Line format in student_name_file:
    # username firstName lastName

    # (key, value) -> (firstNamelastName, username)
    username_dict = {}

    # (key, value) -> ([file1, file2])
    student_name_dict = {}

    for line in open(student_name_file):
        items = line.split(" ")

        username_dict[items[1].strip()+items[2].strip()] = items[0].strip()
        student_name_dict[items[0]] = []

    # File format for files in file_list: 
    # DDDDD-DDDDDDD - lastName, firstName - fileName
    for current_file_name in file_list:

        file = temp_zip_directory_name + "/" + current_file_name

        full_name = (file.split(" - ")[1].strip()).split(", ")
        first_name, last_name = full_name[1].strip(), full_name[0].strip()

        # Grab the original name of the file and rename the current one
        file_name = file.split(" - ")[2].strip()

        user_name = username_dict[first_name+last_name]

        call(["mkdir", file, temp_zip_directory_name + "/" + user_name ], stdout=devnull, stderr=devnull)
        call(["mv", file, temp_zip_directory_name + "/" + user_name + "/" + file_name], stdout=devnull, stderr=devnull)


        student_name_dict[user_name] += [user_name + "/" + file_name]

    return student_name_dict


def move_labs(student_dict, dir_name, temp_zip_directory_name):
    """
    move_labs - moves all of the files from in the temporary directory to the 
        provided directory, creating any student directories if they do 
        not already exist

    @param student_dict the dictionary of students
    @param dir_name the directory to unzip all of the labs into
    @param temp_zip_directory_name name of directory with temp labs
    """
    for user_name in student_dict.keys():

        # Make the student directory
        if not os.path.exists(dir_name + "/" + user_name):
            call(["mkdir", dir_name + "/" + user_name ], 
            stdout=devnull, stderr=devnull)

        # Directory to put the submision into to avoid mixing with 
        # try submissions directories that are already there
        call(["mkdir", dir_name + "/" + user_name + "/Submission"],
            stdout=devnull, stderr=devnull)

        # NOTE: There may be no files to move
        for file in student_dict[user_name]:
            call(["mv", temp_zip_directory_name + "/" + file, 
                dir_name + "/" + user_name + "/Submission"],
                stdout=devnull, stderr=devnull)

def usage():
    """
    prints the usage statement for the script
    """

    print('usage: zipunzipper.py zipfile students dirname')
    print('     zipfile  - The zip file downloaded from myCourses that contains all the labs')
    print('     students - file containing all the students full names and usernames (new line delimited).')
    print('     dirname  - the name of the directory to drop all of the labs (i.e ./course/labs/lab01/')

def main():
    """
    unzips a zip file that contains all the from dropbox and puts them 
        in the correct student directory
    
    first argument is the zip file
    second argument is a list of the students (directories) names
    third argument is the Lab directory
    """

    # Check for valid number of parameters
    if(len(sys.argv) != 4):
        usage()
        exit(1)

    zip_file_name = sys.argv[1]
    student_name_file = sys.argv[2]
    dir_name = sys.argv[3]

    # Check that all arguments passed in are vallid
    if( not os.path.isfile(zip_file_name) or 
        not zip_file_name.endswith('.zip') ):
        
        print('Zip file does not exist or is not a zip file')
        return

    if( not os.path.isfile(student_name_file) ):
        print('Student file does not exist')
        return

    if( not os.path.exists(dir_name) ):
        print('Lab directory does not exist')
        return

    # Create a temp directory to store the unzipped myCourses zip files
    temp_zip_directory_name = "temp_zip_directory"
    if(dir_name.endswith('/')):
        temp_zip_directory_name = dir_name + temp_zip_directory_name
    else:
        temp_zip_directory_name = dir_name + '/' + temp_zip_directory_name
        dir_name = dir_name + '/'

    call(["mkdir", temp_zip_directory_name], stdout=devnull, stderr=devnull)
    call(["unzip", "-d", temp_zip_directory_name, zip_file_name], 
        stdout=devnull, stderr=devnull)

    # New file format: 
    # DDDDD-DDDDDDD - lastName, firstName - fileName

    # Grab all of the zip files that were unzipped from dropbox super zip
    file_list = listdir(temp_zip_directory_name)

    # Remove the "index.html" file from the file_list
    file_list.remove("index.html")

    #create the student dictionary 
    student_dict = get_student_dict(student_name_file, file_list, temp_zip_directory_name)
    sorted_keys = sorted(student_dict.keys())

    # Print out all files and usernames
    for username in sorted_keys:
        print username,
        print(student_dict[username])

    move_labs(student_dict, dir_name, temp_zip_directory_name)

    # Remove the temp directory
    call(["rm", "-r", temp_zip_directory_name], stdout=devnull, stderr=devnull)

main()
