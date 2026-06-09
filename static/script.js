"use strict";

const images = document.querySelectorAll("img");

// needed to use forEach, which is kind of like a for loop that
// gives every image the function: https://www.w3schools.com/jsref/jsref_foreach.asp 
images.forEach(function(img) { 
  img.addEventListener("mouseover", zoomIn);
  img.addEventListener("mouseout", zoomOut);
});

function zoomIn(e) {
  const img = e.target;
  img.classList.toggle("zoom");
}

function zoomOut(e) {
  const img = e.target;
  img.classList.toggle("zoom");
}

const toggleBtn = document.getElementById('theme-toggle');
const themeLink = document.getElementById('theme-link');

const lightTheme = "https://newcss.net/theme/light.css";
const nightTheme = "https://newcss.net/theme/night.css";

toggleBtn.addEventListener('click', () => {
  if (themeLink.getAttribute('href') === lightTheme) {
    themeLink.setAttribute('href', nightTheme);
    toggleBtn.textContent = "Dark Mode";
  } else {
    themeLink.setAttribute('href', lightTheme);
    toggleBtn.textContent = "Light Mode";
  }
});