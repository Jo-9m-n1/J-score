# Content Page by James

## Subtopic: What is the variance, normal distribution and R-score?

The main content page will contain three parts added by me: an explanation of the variance and normal distribution, and an explanation of the R-score and how we programmed the calculator.

<h3> Section 1: Variance </h3>
<p>
A variance shows how far values spread from the mean, which is the average of a sample set. The variance is found by averaging squared differences from that mean. It’s squared to make large deviations count more, highlighting datasets with wide spread. 
</p>

<img alt="Image of variance formula">

<h3> Section 2: Normal distribution </h3>

<p>
A normal distribution is a bell shape chart where most values cluster near the mean and fewer appear at the extremes. A useful rule of thumb is the 68–95–99.7 rule: about 68% of values lie within one standard deviation of the mean, ~95% within two, and ~99.7% within three. This is assuming that the data are approximately near the mean. This lets use probabilities and compare results fairly across classes or tests.
<p>

<img alt="Image of a normal distribution graph">

<h3> Section 3: R-Score </h3>

The R-Score is equal to (Z * IDGZ + IFGZ + 5) * 5.

Here's what every variable means:

- <b>Z = the z-score for a course</b>
  - This is found using (the course grade - the course mean) / the course standard deviation
- <b>IFGZ or ISGZ = l'indicateur de la force du groupe (indicator of the strength of the group)</b>
  - This variable is defined as how good are the high school marks of the students in a <i>CEGEP</i> class.
  - Students in the course are given high school <b>z-scores</b>, which are abased on their academic performance in ministerial high school courses.
  - The <i>IFGZ</i> is the average of these high school <b>z-scores</b>.
  - The range of this value is around [-1.5, 1.5]
  - A higher <b>ISGZ</b> indicates that the course or group tends to have lower averages or tougher grading, which raises everyone’s R-Scores slightly to maintain fairness and consistency across colleges.
- <b>IDGZ = l'indicateur de la dispersion du groupe </b>
  - This variable measures the dispersion of the high school <b>z-scores</b> of a student compared to their classmates for a course. It's the standard deviation of high-school <b>z-scores</b>.
  - In other words, it measures how diverse the highest marks of students in a <i>CEGEP</i> class.
  - The range of this value is around [0, 1.5]
  - A higher <b>IDGZ</b> means that your classmates, on average, performed very well before entering that course. In other words, you’re in a stronger group.
- <b>The two mysterious 5 constants </b>
  - The first 5 (the "+ 5") reduces the possibility of a negative value in the score, which the second 5 (the "* 5") ensures the largeness of the score.
  - The R-score range is [0, 50] but most fall into [15, 35].
  - Grades below 50 are not considered in calculating the average and the standard deviation fo a grade distribution.

<h4>Why is it difficult to calculate an <i>accurate</i> R-Score?</h4>
<p>
The <i>IFGZ</i> and <i>IDGZ</i> are the <b>only</b> constants that are difficult to find without the prior data from High School. This data is protected by the Ministry of Education and the <i>Bureau de coopération interuniversitaire (BCI).</i> Therefore, these variables vary tremendously. As students, we cannot get these exact values and without those exact numbers, you can only estimate your R-score.
</p>

<h4>How do we estimate your R-Score?</h4>

- The <b>IDGZ</b> is determined by the College class taken. 
    - If a student took a science concentration course for their program, the student is rewarded a higher <b>IDGZ</b>. It's because it's highly probable that the students taking that science class has higher overall grades. These grades usually don't have much difference from the average and the standard deviation is kept relatively low. 
    - If a student took a general education class, such as english, french, humanities, and gym, then they will have a lower <b>IDGZ</b> value. It's very probable that the students in that specific class come from any program, where student's overall grade is very varied. This means that the standard deviation is higher than a science class.
- The <b>ISGZ</b> is determined by three variables: a guess done by the user of the class's high school average, an average high school grade in the province, and the average standard deviation in the province. It's using the <b>Z-score</b> formula, which helps determine whether the class performed stronger or weaker than the average Quebec student group, which is then reflected in the <b>ISGZ</b> adjustment.

#### Citations for above text/media

- [QUÉtudes-info!](https://quetudesinfo.vercel.app/whatiscegep/therscore)

- [Wikipedia](https://en.wikipedia.org/wiki/R_score)

#### Custom CSS

- `.cards`
- `.section` {
    display:flex:
    gap:16px;
    align-items:flex-start;
}
- `nav` {
  display:flex; gap:12px;
}

### [Link to design image](designs/contentproposaldesign.png)
