#! /usr/bin/python

import MySQLdb, cgi, sys, getopt, subprocess, os.path

############################    DOCUMENTATION     #############################
# DESCRIPTION:
#   Grapefruilt_Webwork_API that allows adding users directly to the database
#   without needing to be logged into webwork as an instructor. It can be
#   called from the command line or a get/post command.
#
# SYNOPSIS:
#   CMD LINE:
#     AddUser.py -c|--course= <course> -u|--user= <user_id>
#                -s|--student= <student_id> [-p|--password= <password>]
#                [-e|--email= <email_address>] [-f|--first_name= <first_name>]
#                [-l|--last_name <last_name>] [-m|--permission= <permission_#>]
#                [-t|--section= <section_#>] [-r|--recitation= <recitation_#>]
#                [--comment= "<comment>"]
#   CGI CALL:
#     <untested. please test & insert call here.>
# DEPENDANCY:
#   MySQLdb module needs to be downloaded:
#     Linux: sudo apt-get install python-mysqldb
#   webworkCrypt.pl file must be in the same directory for password encryption.
#
# AUTHORS:
#   Kevin L. Mahon
#   Kate Spinney


##############################    FUNCTIONS     ###############################

# Adds a user to the webwork database.
# Edits the [course_name]_user, [course_name]_password, and [course_name]_permissions tables.
# Returns 0 on failure and 1 on success.
def addUser(course_name, user_id, first_name, last_name, email_address, student_id, section, recitation, comment, password, permission):
	# Attempt to make connection to the webwork database.
	# Exits function returning 0 if failure.
	try:
		db = MySQLdb.connect("localhost", "root", "wwadmin", "webwork")
		cursor = db.cursor()
	except:
		print "ERROR: Could not connect to webwork database."
		return 0;

	userTableSQL = "INSERT INTO " + course_name + "_user(user_id, first_name, last_name, email_address, student_id, section, recitation, comment) VALUES (" + user_id + ", " + first_name + ", " + last_name +", " + email_address +", " + student_id + ", " + section + ", " + recitation + ", " + comment + ")"
	passwordTableSQL = "INSERT INTO " + course_name + "_password(user_id, password) VALUES (" + user_id + ", " + password + ")"
	permissionTableSQL = "INSERT INTO " + course_name + "_permission(user_id, permission) VALUES (" + user_id + ", " + permission + ")"


	# Attempts to add and commit SQL commands.
	#Rolls back and prints SQL error message if fails.
	try:
		cursor.execute(userTableSQL)
		cursor.execute(passwordTableSQL)
		cursor.execute(permissionTableSQL)
		db.commit()
		return 1;
	except MySQLdb.Error, error:
		try:
			print "MySQL Error [%d]: %s" % (error.args[0], error.args[1])
		except IndexError:
			print "MySQL Error: %s" % str(error)
		db.rollback()
		return 0;

	# Close the database connection
	db.close()


###############################   MAIN   ######################################

# Initialize varibles to default values
course = None
user_id = None
student_id = None
password = None
first_name = "NULL"
last_name = "NULL"
email = "NULL"
section = "NULL"
recitation = "NULL"
comment = "NULL"
permission = "\"0\""

# Reads parameters in from the CGI object if passed vai a get/post call
form = cgi.FieldStorage()
if form.getvalue("course", None) is not None and form.getvalue("user_id", None) is not None and form.getvalue("student_id",None) is not None:
	course = form.getvalue("course")
	user_id = "\"" + form.getvalue("user_id") + "\""
	student_id = "\"" + form.getvalue("student_id") + "\""
	if form.getvalue("first_name", None) is not None:
		first_name = "\"" + form.getvalue("first_name") +"\""
	if form.getvalue("last_name", None) is not None:
		last_name = "\"" + form.getvalue("last_name") + "\""
	if form.getvalue("email", None) is not None:
		email = "\"" + form.getvalue("email_address") + "\""
	if form.getvalue("section", None) is not None:
		section = "\"" + form.getvalue("section") + "\""
	if form.getvalue("reciation", None) is not None:
		recitation = "\"" + form.getvalue("recitation") + "\""
	if form.getvalue("comment", None) is not None:
		comment = "\"" + form.getvalue("comment") + "\""
	if form.getvalue("password", None) is not None:
		password = form.getvalue("password")
	permission = "\"" + form.getvalue("permission", "0") + "\""
# Reads parameters in from command line
elif len(sys.argv) > 1:
	# Parameters from command line are read as options.
	try:
		opts, args = getopt.getopt(sys.argv[1:],"c:f:e:l:m:p:r:s:t:u:",["comment=","course=","email=","first_name=","last_name=","password=", "permission=","recitation=","section=","student=","user="])
	except getopt.GetoptError:
		print 'AddUser.py -c|--course= <course> -u|--user= <user_id> -s|--student= <student_id> [-p|--password= <password>] [-e|--email= <email_address>] [-f|--first_name= <first_name>] [-l|--last_name <last_name>] [-m|--permission= <permission_#>] [-t|--section= <section_#>] [-r|--recitation= <recitation_#>] [--comment= "<comment>"]'
		sys.exit()

	for opt, arg in opts:
		if opt in ("-c", "--course"):
			course = arg
		elif opt in ("-u", "--user"):
			user_id = "\"" + arg + "\""
		elif opt in ("-s", "--student"):
			student_id = "\"" + arg + "\""
		elif opt in ("-p", "--password"):
			password = arg
		elif opt in ("-e", "--email"):
			email = "\"" + arg + "\""
		elif opt in ("-f", "--first_name"):
			first_name = "\"" + arg + "\""
		elif opt in ("-l", "--last_name"):
			last_name = "\"" + arg + "\""
		elif opt in ("-r", "--recitation"):
			recitation = "\"" + arg + "\""
		elif opt in ("-m", "--permission"):
			permission = "\"" + arg + "\""
		elif opt in ("-t", "--section"):
			section = "\"" + arg + "\""
		elif opt == "--comment":
			comment = "\"" + arg + "\""

	# If mandatory options are not specified, print error message
	if course is None or user_id is None or student_id is None:
		print 'ERROR: course, student, & user are required options'
		print 'AddUser.py -c|--course= <course> -u|--user= <user_id> -s|--student= <student_id> [-p|--password= <password>] [-e|--email= <email_address>] [-f|--first_name= <first_name>] [-l|--last_name <last_name>] [-m|--permission= <permission_#>] [-t|--section= <section_#>] [-r|--recitation= <recitation_#>] [--comment= "<comment>"]'
		sys.exit()

# If manatory variables are not changes from NULL value, throw error & exit
if course is None or user_id is None or student_id is None:
	print 'ERROR: course_name, student_id, & user_id are required'
	sys.exit()

# Change password to user_id if no password was specified
# This is done to mimic the webwork code as closely as possible
if password is None:
	password = user_id.replace("\"","")

# <INSERT CALL TO WEBWORK'S cryptPassword(password) FUNCTION IN /opt/webwork/webwork2/lib/WeBWorK/Utils.pm HERE>
if os.path.isfile('./webworkCrypt.pl'):
	password = "\"" + subprocess.check_output("perl ./webworkCrypt.pl " + password, shell=True) + "\""

addUser(course, user_id, first_name, last_name, email, student_id, section, recitation, comment, password, permission)
