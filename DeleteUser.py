#! /usr/bin/python

import MySQLdb, cgi, sys, getopt, subprocess, os.path

# CONNECT TO DATABASE
try:
	db = MySQLdb.connect("localhost", "root", "wwadmin", "webwork")
	cursor = db.cursor()
except:
	print "ERROR: Could not connect to webwork database."

# GET COMMAND LINE ARGUMENTS
courseName = sys.argv[1]
userId = sys.argv[2]

# SQL REQUESTS:
try:
	cursor.execute("DELETE FROM " + courseName + "_user WHERE user_id='" + userId + "'")
	cursor.execute("DELETE FROM " + courseName + "_password WHERE user_id='" + userId + "'")
	cursor.execute("DELETE FROM " + courseName + "_permission WHERE user_id='" + userId + "'")
	cursor.execute("DELETE FROM " + courseName + "_achievement_user WHERE user_id='" + userId + "'")
	cursor.execute("DELETE FROM " + courseName + "_global_user_achievement WHERE user_id='" + userId + "'")
	cursor.execute("DELETE FROM " + courseName + "_key WHERE user_id='" + userId + "'")
	cursor.execute("DELETE FROM " + courseName + "_past_answer WHERE user_id='" + userId + "'")
	cursor.execute("DELETE FROM " + courseName + "_problem_user WHERE user_id='" + userId + "'")
	cursor.execute("DELETE FROM " + courseName + "_set_locations_user WHERE user_id='" + userId + "'")
	cursor.execute("DELETE FROM " + courseName + "_set_user WHERE user_id='" + userId + "'")
except MySQLdb.Error, error:
	try:
		print "MySQL Error [%d]: %s" % (error.args[0], error.args[1])
	except IndexError:
		print "MySQL Error: %s" % str(error)
	db.rollback()
