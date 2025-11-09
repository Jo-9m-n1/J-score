# Feature Page by James

## Subtopic: R-Score Calculator

I will be implementing an R-Score calculator that will allow users, who would mostly be students, to get an approximation of their R-Score in a Cegep course. The user can also find their overall R-score from the weighted average of all individual R-scores and their respective credits.

The variables that I'll need to accomplish this calculator are the user's overall grade in a course, the class average grade, the class's standard deviation, the type of class taken, which is either a science concentration-specific course (such as General Chemistry and Calculus) or a general education class (such as English and French), a guess of the class's high school average, and the number of credits associated with the course, which is determined from the number of hours of classes in a week. Additionally, we will be asking the user for the name of the class/course.

All values will be retrieved from the user input using a `request.form.get()` for each variable. There will be one or maybe two functions to calculate the R-score. This will also include a Z-score formula to approximate one unknown variable (ISGZ) with the average high school grade in the province and the average standard deviation in the province. The ISGZ is unknown to us and to the user, since it's coming from the Ministry of Education. Once the R-score is calculated, it will be stored in an “r-scores.csv” file and displayed along with the course name on a design table.

This table will include a button to remove the latest R-score posted on the table. This is there in case the user makes a mistake. This can be done by going into read mode in the CSV file with Python, getting all the lines into a Python variable, slicing the last row, and then using write mode in the CSV file to write the updated Python variable.

Every time the user enters new data, the page will also show the updated overall R-score from the weight (credits). This can be done by first opening the CSV file and reading all the data with “csv.reader.” The strings must then be converted as floats and put into a list so that the average overall R-score can be quickly determined.