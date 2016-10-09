#!/usr/bin/python
"""
break-up-comments.py - given a comments file for a lab/homework/project, 
  breaks up the comments into separate files for each different activity for 
  each user;  This is so they can be more easily graded on the try system.

  NOTE: The comments file should be formatted as seen in labtemplate.txt
  NOTE: The students file should be formatted as seen in studentstemplate.txt

Usage: break-up-comments.py <student_file> <comments_file>")
  students_file - The file containing all of the student's usernames")
  comments_file - The file containing all the comments for all students 
                  (formatted correctly")

After running, the script should create a directory with all the broken up 
comments, as well as a zip of all the comments that you can copy over to the 
grader account

Author: T. Wilgenbusch
"""


import sys
import os.path

from subprocess import call, check_output
from os import listdir
from os.path import basename

def make_activity_comments_file(cur_activity, student, activity_count):
    """
    make_activity_comments_file makes a file for a student's activity comments 
    in the current directory

    Should look like the following:
        stu0000-comment-1.txt

    cur_activity the content of the file
    student the username of the student
    activity_count the current activity being made
    """
    call(["touch", student + "-comment" + "-" + str(activity_count) + ".txt"])
    f = open(os.getcwd() + "/" + student + "-comment" + "-" + str(activity_count) + ".txt", 'w')
    f.write(cur_activity)
    f.close()

def parse_comments(all_comments, studs):
    """
    parse_comments given an array of lines, parses them into seperate 
    activities for each student and then creates a file holding those activity 
    comments

    all_comments a list containing all the lines for a comment file
    studs a list of student usernames
    """
    i = 0
    cur_line = all_comments[i]

    #Go through all comments
    while(i < len(all_comments)):
        cur_line = all_comments[i]

        #Only start parsing comments that start with the student's username
        if(all_comments[i] in studs):
            #grab the student's username
            student = cur_line.strip()

            i += 1
            #The activity number that we will be parsing (Starts with 1)
            activity_count = 1

            #This is to grab all of the comments for a specfic student (probably no longer needed)
            while(i < len(all_comments) and all_comments[i] not in studs):

                #parsing for a specific activity for the student
                #The line should look like 'Activity #'
                if(("Activity " + str(activity_count)) in all_comments[i]):
                    #holds the comments for the current activity for the current student
                    cur_activity = ""

                    #We want to keep parsing until one of the following occurs:
                    #   a. We reach the end of the file
                    #   b. We find the next activity header
                    #   c. We reach the next student's comment section
                    while(i < len(all_comments) and 
                        ("Activity " + str(activity_count + 1)) not in all_comments[i] and 
                        all_comments[i] not in studs):

                        #Add the current line to the activity comments and move to the next line
                        cur_activity += all_comments[i]
                        i += 1

                    #After we've gotten all of the current activity collected, 
                    #make the text file for that activity
                    make_activity_comments_file(cur_activity, student, activity_count)

                    #increment the activity_count
                    activity_count += 1
                    #Move the index back by one so that we can collect the next 
                    #Activity if we missed it by moving to far forward
                    i -= 1
                
                i += 1
        
        #Move on until we find a student's comments
        else:
            i += 1  

def main():
    """
    main - asks for user input and creates the comment files
    """

    #Script requires at least three command line arguments
    if(len(sys.argv) != 3):
        usage()
        return
    
    #The file containing the user ids of the students
    students_file = sys.argv[1]
    #The file containing the comments for a paticular assignment
    comments_file = sys.argv[2]

    if (not os.path.isfile(students_file)):
        print("students_file is not a file")
        usage()
        return

    if (not os.path.isfile(comments_file)):
        print("comments_file is not a file")
        usage()
        return

    all_comments = []
    studs = []

    #Grab all of the student names
    for line in open(students_file):
        studs += [line]
    #Grab all of the comment lines
    for line in open(comments_file):
        all_comments += [line]


    #Make the directory that will hold all of the files to zip, then change into that directory
    call(["mkdir", os.getcwd() + "/" + basename(comments_file) + "-zip"])
    os.chdir(os.getcwd() + "/" + basename(comments_file) + "-zip")
    
    #parse all comments into seperate activities and create files for each activity
    parse_comments(all_comments, studs)

    os.chdir("../")
    call(["zip", "-r", "labcomments", "./" + basename(comments_file) + "-zip"])

def usage():
    """
    usage - prints usage message on bad input
    """
    print("break-up-comments.py student_file comments_file")
    print("     students_file - The file containing all of the student\'s usernames")
    print("     comments_file - THe file containing all the comments for all atudents (formatted correctly)")

main()