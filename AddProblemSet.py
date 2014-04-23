#! /usr/bin/python

import MySQLdb, sys, os, shutil, pwd, argparse, time

############################    DOCUMENTATION     #############################
# DESCRIPTION:
#   
# NOTE:
#   
# USAGE:
#   AddProblemSet.py 
# AUTHORS:
#   Kevin L. Mahon

###############################   MAIN   ######################################


##### VARIABLE/PERMISSION SETTING #####

# Get default times
timeUTC = int(time.time())
open_default = timeUTC + 604800
due_default = timeUTC + 1209600
answer_default = timeUTC + 1814400

# Parse arguments using argparse module (https://docs.python.org/2/library/argparse.html)
parser = argparse.ArgumentParser(description='Grapefruit to Webwork2 API:')
parser.add_argument('courseName', help="Name of the course the problem will be in")
parser.add_argument('setName', help="Name of the problem set to be added")
parser.add_argument('--set_header', default="defaultHeader", help="Location of header file to use. File will be copied to correct spot in webwork file system.")
parser.add_argument('--hardcopy_header', default="defaultHeader", help="Location of hardcopy header file to use. File will be copied to correct spot in webwork file system.")
parser.add_argument('-o', '--open_date', default=open_default, help='Date the problem set will be available to students. Value should be the # of seconds from epoch UTC. Default value is 1 week from current time.')
parser.add_argument('-d', '--due_date', default=due_default, help='Date students must finish the problem set by. Value should be the # of seconds from epoch UTC. Default value is 2 weeks from current time.')
parser.add_argument('-a', '--answer_date', default=answer_default, help='Date the problem set answers will be available to students. Value should be the # of seconds from epoch UTC. Default value is 3 weeks from curren time.')
parser.add_argument('-v', '--visible', choices=[0, 1], default=1, help="Makes problem set visible when inactive. 0 = invisible & 1 = visible. Default is 1.")
args = parser.parse_args()

# Other Variables
courseDir = "/opt/webwork/courses/" + args.courseName + "/templates"

# Connect to Webwork Database
try:
	db = MySQLdb.connect("localhost", "root", "wwadmin", "webwork")
	cursor = db.cursor()
except:
	print("ERROR: Could not connect to webwork database.")
	sys.exit()


##### ERROR CHECKING #####

# Check that course exists in directory
if( not os.path.isdir(courseDir) ):
	sys.stderr.write("ERROR: AddProblemSet.py could not add set to course directory /opt/webwork/courses/" + args.courseName + "/templates. The directory does not exist.\n")
	sys.exit()

if( os.path.isdir(courseDir + "/set" + args.setName) ):
	sys.stderr.write("ERROR: AddProblem.py could not add problem set. Problem set directory already exists.\n")
	sys.exit()


##### ADDING THE PROBLEM SET #####

try:
	cursor.execute("INSERT INTO " + args.courseName + "_set(set_id, set_header, hardcopy_header, open_date, due_date, answer_date, visible) VALUES (\"" + args.setName + "\", \"" + args.set_header + "\", \"" + args.hardcopy_header + "\", " + str(args.open_date) + ", " + str(args.due_date) + ", " + str(args.answer_date) + ", " + str(args.visible) + ")")
	os.mkdir(courseDir + "/set" + args.setName)
	with open(courseDir + "/set" + args.setName + ".def", "w+") as setDefFile:
		setDefFile.write("setNumber=set" + args.setName + "\n")
		setDefFile.write("openDate = " + time.strftime('%m/%d/%Y at %I:%M%p', time.localtime(args.open_date)) + "\n")
		setDefFile.write("dueDate = " + time.strftime('%m/%d/%Y at %I:%M%p', time.localtime(args.due_date)) + "\n")
		setDefFile.write("answerDate = " + time.strftime('%m/%d/%Y at %I:%M%p', time.localtime(args.answer_date)) + "\n")
		setDefFile.write("paperHeaderFile = " + args.set_header + "\n")
		setDefFile.write("screenHeaderFile = " + args.hardcopy_header + "\n")
		setDefFile.write("\n")
		setDefFile.write("problemList=\n")
	db.commit()
except MySQLdb.Error, error:
	try:
		print "MySQL Error [%d]: %s" % (error.args[0], error.args[1])
	except IndexError:
		print "MySQL Error: %s" % str(error)
	db.rollback()

db.close()
