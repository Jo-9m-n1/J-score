# Content Page by Jongmin
Admissions probability calculator

## Subtopic: TITLE
Admissions probability calculator

### Text and media in the main content area

<h1>Understanding Normal Distribution, Standard Deviation and Z-Scores</h1>
<h2>Normal distriubtion</h2>
<p>In statistics, "normal distribution" is often called the "bell curve"</p>
<img alt="Image of a normal distribution graph">
<h2>Standard Deviation</h2>
<p>
    The standard deviation is the most common measure of data variability. A small
    standard deviation means that the data points are clustered near the mean, 
    showing a low variability. A large standard deviation means that the data is widely 
    spread out. The empricial rule states that 68% of all data falls within a standard 
    deviation of the mean.
</p>
<h2>Z-score (Standard Score)</h2>
<p>
    The Z-score measures how many standard deviations a chosen data point is above or 
    below the mean.
</p>
<img alt="Z-score formula">
<p>
    The Z-score allows us to compare data. By converting each data point to Z-scores, 
    we can see how far away each data point is located from the standard deivation. 
    A positive Z-score indicates that the choosen data is above the average and a 
    negative means it is below.
</p> 
<h2>Application in the Admissions Calculator</h2>
<p>
    Our admissions calculator uses the Z-score to calculate your chances of getting
    in to your dream college. We use the propertieis of a normal distribution, assuming 
    that the the mean is 0.025 below the historical cut-off score. Once you input your 
    R-score, our calculator standardizes it into a Z-score. This Z-score is then mapped
    to a percnetile on the standard cure, providing you with a statistically approximated
    probability.
</p>
#### Citations for above text/media

- This image is from <a href="https://mathbitsnotebook.com/Algebra2/Statistics/STzScores.html">source</a>, 
used under fair dealing for educational purposes
- This image is from <a href="https://www.standarddeviationcalculator.io/storage/2023/May/Zscore_39.png">source</a>,
used under fair dealing for educational purposes

#### Custom CSS

a:hover {
    background-color: #b4bcd2;
    color:#4b6bba;
    border-radius: 10px;
}

img {
    flex-shrink: 0;
}

body {
    margin: 0 auto;
}

### Link to design image

TO INCLUDE:
- header that matches homepage
- nav that matches homepage and other content pages
<header>
    <h1>
            <a href="{{ url_for('index')}}">J-score*</a>
    </h1>
    <nav>
        <ul>
            <li><a href="{{ url_for('admissions') }}">Go to Admissions Page</a></li>
            <li><a href="{{ url_for('r_score') }}">Calculate your R-score</a></li>
        </ul>
    </nav>
</header>

- footer with citations for media/content specific to the Page
<footer>
    <p>
        This image is from <a href="https://mathbitsnotebook.com/Algebra2/Statistics/STzScores.html">source</a>, 
        used under fair dealing for educational purposes
    </p>
    <p>
        This image is from <a href="https://www.standarddeviationcalculator.io/storage/2023/May/Zscore_39.png">source</a>,
        used under fair dealing for educational purposes
    </p>
</footer>