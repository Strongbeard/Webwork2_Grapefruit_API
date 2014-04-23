#! /usr/bin/python

import MySQLdb, sys, os, shutil, pwd, argparse, gzip

############################    DOCUMENTATION     #############################
# DESCRIPTION:
#   Takes a problem file and adds it to the problem set in both the file system
#   and the Webwork database. The name of the course the problem will be added
#   to, the problem ID #, and the new name of the problem must also be
#   specified. Optional arguments include the maximum # of attempts webwork
#   allows for the problem, how much the problem is worth to the webwork
#   scoring algorithm, and flags that are stored in the webwork database.
#   Look up the possible values of the flags in the Webwork documentation.
# NOTE:
#   The user must be either root or www-data for this file to run.
# USAGE:
#   AddProblem.py [-h] [-m MAX_ATTEMPTS] [-v VALUE] [-f FLAGS] courseName
#                 problemSet problemPath problemName problemId
# AUTHORS:
#   Kevin L. Mahon

###############################   MAIN   ######################################


##### VARIABLE/PERMISSION SETTING #####

# Parse arguments using argparse module (https://docs.python.org/2/library/argparse.html)
parser = argparse.ArgumentParser(description='Grapefruit to Webwork2 API: adds a problem .pg file to a problem set in Webwork.')
parser.add_argument('courseName', help="Name of the course the problem will be in")
parser.add_argument('problemSet', help="Name of the problem set the problem will be in")
parser.add_argument('problemPath', help="Path to the source problem file. This will be copied to the problem set directory")
parser.add_argument('problemName', help="New name of the problem")
parser.add_argument('problemId', help="Problem ID for webwork database. Should be unique per problem set.")
parser.add_argument('-m', '--max_attempts', default='-1', help="Maximum number of attemps students have to answer problem. No input sets max attempts to infinity.")
parser.add_argument('-v', '--value', default='1', help="Value of the problem used in Webwork's scoring algorithm")
parser.add_argument('-f', '--flags', default="NULL", help="Flags stored in Webwork's database. Don't know what they do. Look at the webwork documentation.")
args = parser.parse_args()

# Other Variables
user = pwd.getpwuid( os.getuid() )[0]
courseDir = "/opt/webwork/courses/" + args.courseName + "/templates"
decompressed = False

# Connect to Webwork Database
try:
	db = MySQLdb.connect("localhost", "root", "wwadmin", "webwork")
	cursor = db.cursor()
except:
	print("ERROR: Could not connect to webwork database.")
	sys.exit()


##### ERROR CHECKING #####

# Checks that user has sufficient permissions to add data
if( not ( user == "root" or user == "www-data" ) ):
	sys.stderr.write("ERROR: AddProblem.py insufficient permissions to add a problem to a course.\n\tPlease run AddProblem.py as www-data or root.\n")
	sys.exit()

# Check that course exists in directory
if( not os.path.isdir(courseDir) ):
	sys.stderr.write("ERROR: AddProblem.py could not add problem to course directory /opt/webwork/courses/" + args.courseName + "/templates. The directory does not exist.\n")
	sys.exit()

# Checks that the problem set directory & definition file exists
if( not ( os.path.isdir(courseDir + "/set" + args.problemSet) and os.path.isfile(courseDir + "/set" + args.problemSet + ".def") ) ):
	sys.stderr.write("ERROR: AddProblem.py could not find the problem set directory.\n")
	sys.exit()

# Checks that path to source file is valid
if( not os.path.isfile(args.problemPath) ):
	sys.stderr.write("ERROR: AddProblem.py invalid path to new problem file.\n\tPlease specify the path of the source file you want transfered to the course directory as the 3rd argument.\n")
	sys.exit()


##### ADDING THE PROBLEM #####

# File added to the problem set directory will always have .pg on the end
if( not args.problemName.split(".")[-1] == "pg" ):
	args.problemName += ".pg"
destPath = courseDir + "/set" + args.problemSet + "/" + args.problemName

try:
	# Add problem to webwork database
	cursor.execute("INSERT INTO " + args.courseName + "_problem(set_id, problem_id, source_file, value, max_attempts, flags) VALUES (\"" + args.problemSet + "\", \"" + args.problemId + "\", \"" + destPath + "\", \"" + args.value + "\", \"" + args.max_attempts + "\", " + args.flags + ")")
	# Copy file to problem set folder
	shutil.copyfile(args.problemPath, destPath)
	# Add file to problem set definition page
	with open(courseDir + "/set" + args.problemSet + ".def", "a") as setDefFile:
		setDefFile.write(args.problemSet + "/set" + args.problemName + ".pg,   1")
	db.commit()
except MySQLdb.Error, error:
	try:
		print "MySQL Error [%d]: %s" % (error.args[0], error.args[1])
	except IndexError:
		print "MySQL Error: %s" % str(error)
	db.rollback()

# Close the database connection
db.close()
