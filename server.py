
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "jl5447"
DATABASE_PASSWRD = "814543"
DATABASE_HOST = "35.212.75.104" # change to 34.28.53.86 if you used database 2 for part 2       Originally: 34.148.107.47
#Original : DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1" 
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2" 


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


@app.route('/')
def index():
	select_query = "SELECT * from timeslots"
	cursor = g.conn.execute(text(select_query))
	timeslots = []
	columns = cursor.keys()
	for result in cursor:
		timeslot_dict = {}
		for column, value in zip(columns, result):
			timeslot_dict[column] = value
		timeslots.append(timeslot_dict)
	cursor.close()

	select_query = "SELECT * from course"
	cursor = g.conn.execute(text(select_query))
	courses = []
	columns = cursor.keys()
	for result in cursor:
		course_dict = {}
		for column, value in zip(columns, result):
			course_dict[column] = value
		courses.append(course_dict)
	cursor.close()
	
	select_query = "SELECT * from program"
	cursor = g.conn.execute(text(select_query))
	programs= []
	columns = cursor.keys()
	for result in cursor:
		program_dict = {}
		for column, value in zip(columns, result):
			program_dict[column] = value
		programs.append(program_dict)
	cursor.close()

	select_query = "SELECT * from plans where student_id=1" 
	cursor = g.conn.execute(text(select_query))
	plans= []
	columns = cursor.keys()
	for result in cursor:
		plans_dict = {}
		for column, value in zip(columns, result):
			plans_dict[column] = value
		plans.append(plans_dict)
	cursor.close()

	course_ids_with_sections = [(plan['course_id'], plan['section']) for plan in plans]
	print("course_ids_with_sections: ", course_ids_with_sections)

	chosen_courses= []
	for course_id, section in course_ids_with_sections:
		select_query = "SELECT * FROM course WHERE course_id = :course_id AND section = :section"
		cursor = g.conn.execute(text(select_query), {'course_id': course_id, 'section': section})
		columns = cursor.keys()
		for result in cursor:
			chosen_courses_dict = {}
			for column, value in zip(columns, result):
				chosen_courses_dict[column] = value
		chosen_courses.append(chosen_courses_dict)
	cursor.close()


	# print("timeslots: ", timeslots)
	# print("programs: ", programs)
	# print("courses: ", courses)
	# print("plans: ", plans)
	print("chosen_courses: ", chosen_courses )

	# Sort the list of dictionaries by start_time
	sorted_timeslots = sorted(timeslots, key=lambda x: x['start_time'])

	# Remove duplicates based on start_time
	unique_timeslots = []
	seen_start_times = set()
	for timeslot in sorted_timeslots:
		start_time = timeslot['start_time']
		if start_time not in seen_start_times:
			unique_timeslots.append(timeslot)
			seen_start_times.add(start_time)

# unique_timeslots now contains the ordered list of dictionaries without duplicates


	return render_template("index.html", timeslots=unique_timeslots, classes_chosen=chosen_courses, programs=programs, classes=courses)


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	name = request.form['name']
	
	# passing params in for each variable into query
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')

# Example of adding new data to the database
@app.route('/add_class/<int:course_id>/<int:section>', methods=['POST'])
def add_class(course_id, section):

	select_query = "SELECT * from plans where student_id=1" 
	cursor = g.conn.execute(text(select_query))
	plans= []
	columns = cursor.keys()
	for result in cursor:
		plans_dict = {}
		for column, value in zip(columns, result):
			plans_dict[column] = value
		plans.append(plans_dict)
	cursor.close()

	course_ids_with_sections = [(plan['course_id'], plan['section']) for plan in plans]

	def exists_in_list(course_id, section, list_of_tuples):
		for tup in list_of_tuples:
			if tup == (course_id, section):
				return True
		return False

	exists = exists_in_list(course_id, section, course_ids_with_sections)
	
	if not exists:
		params = {}
		params["student_id"] = 1
		params["schedule_id"] = 2
		params["course_id"] = course_id
		params["section"] = section
		g.conn.execute(text('INSERT INTO plans(student_id, schedule_id, course_id, section) VALUES (:student_id, :schedule_id, :course_id, :section)'), params)
		g.conn.commit()
	return redirect('/')


@app.route('/remove_class/<int:course_id>/<int:section>', methods=['POST'])
def remove_class(course_id, section):

	select_query = "SELECT * from plans where student_id=1" 
	cursor = g.conn.execute(text(select_query))
	plans= []
	columns = cursor.keys()
	for result in cursor:
		plans_dict = {}
		for column, value in zip(columns, result):
			plans_dict[column] = value
		plans.append(plans_dict)
	cursor.close()

	course_ids_with_sections = [(plan['course_id'], plan['section']) for plan in plans]

	def exists_in_list(course_id, section, list_of_tuples):
		for tup in list_of_tuples:
			if tup == (course_id, section):
				return True
		return False

	exists = exists_in_list(course_id, section, course_ids_with_sections)
	
	if exists:
		params = {}
		params["student_id"] = 1
		params["schedule_id"] = 2
		params["course_id"] = course_id
		params["section"] = section
		g.conn.execute(text('DELETE FROM plans WHERE student_id = :student_id AND schedule_id = :schedule_id AND course_id = :course_id AND section = :section'), params)
		g.conn.commit()
	return redirect('/')

@app.route('/login')
def login():
	abort(401)
	this_is_never_executed()


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()

