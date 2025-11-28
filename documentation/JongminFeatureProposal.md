I would like to add server side feature that sends the user to an 
error page or a result page depending on the user's input. The validation will be
done through flask to ensure that the data is safe and correct, since the 
client-side validation can easliy be eidted or disabled using the browser dev 
tools. If user inputs a string for the cutt-off or the their global r-socre, 
they will be driected to an error page where the user can know which invlaid 
input the user has submitted and will be asked to submit it once more. On the 
other side, when the user inputs everything correctly, they will be driected to 
the result page where it will display their chance of getting in to their dream 
university with their current global r-score. This chance will be calculated 
through flask as well by importing math. We will use the z-score normal 
distribution graph, assuming that the mean is approximately near the cut-off 
grade. With the user's data point (their r-score), the python function will 
calculate the percentile of the user. Which will then be shown to the user as 
their probability of making it in to the college.