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

const savedTheme = localStorage.getItem('selected-theme');
const lightTheme = "https://newcss.net/theme/light.css";
const nightTheme = "https://newcss.net/theme/night.css";
const themeLink = document.getElementById('theme-link');

if (savedTheme && themeLink) {
  themeLink.setAttribute('href', savedTheme);
}

document.addEventListener('DOMContentLoaded', () => {
  const toggleIcon = document.getElementById('theme-toggle');

  if (toggleIcon) {
    toggleIcon.addEventListener('click', (e) => {
      if (toggleIcon.tagName === 'A') e.preventDefault(); 
            
      const currentTheme = themeLink.getAttribute('href');
      if (currentTheme === lightTheme) {
        themeLink.setAttribute('href', nightTheme);
        localStorage.setItem('selected-theme', nightTheme);
      } else {
        themeLink.setAttribute('href', lightTheme);
        localStorage.setItem('selected-theme', lightTheme);
      }
    });
  }
});