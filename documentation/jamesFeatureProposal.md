# Feature Page by James

## Subtopic: R-Score Calculator

Describe the JS and/or server-side feature you want to add to your team’s project, making sure that it is different from but compatible with what the rest of your team is proposing - showcase your web development knowledge!

I will be implementing an R-Score calculator that will allow users, which would mostly be students, to get an approximation of their R-Score in a Cegep course. The user can also find their overall R-Score from the weighted average of all individual R-Scores and their respective credits.

The variables that I'll need to accomplish this calculator are the user's overall grade in a course, the class average grade, the class's standard deviation, and the amount of credits associated with the course, which is determined from the number of hours of classes in a week. Additionally, we will be asking the user for the name of the class/course.

All values will be retrieved from the user input using a `request.form.get()` for each variable. There will be one or maybe two functions to calculate the R-score. This will also include a polynomial formula to approximate one unknown variable (ISGZ). This variable is unknown to us and to the user, since it's coming from the Ministry of Education. Once the R-score is calculated, it will be stored in a dictionary and displayed along with the course name on a table.

This table will include a button to remove the latest R-Score posted on the table. This is there in case the user does a mistake.

The page is also going to display the updated overall R-Score from the weight (credits) everytime the user reenters new data.
