PostgreSQL account: jl5447

url for web app: http://34.74.152.48:8111/


This web app followed our original plan of creating a platform for class schedules. 
Due to the contingency plan and my partner dropping, I only foucsed on classes in the Computer Science Major.
The user is able to view all availbale classes. They are presented with a schedule with the timeslots of each day,
and they are able to easily add and remove courses from their schedule. Once added, the course is shown in the appropriate
timeslot in the visual schedule.

A future goal is to implement the ability to filter classes by major.


I found the most interesting sql query to be associated with the visual of the schedule. I was required to use the 
plans table to join the courses, students, and timeslots tables to display the appropriate data.

Another interesting SQL operation was receiving the timeslots in ascending order so that they would appear properly on 
the schedule and removing duplicates.
