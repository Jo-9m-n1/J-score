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

const lightTheme = "https://newcss.net/theme/light.css";
const nightTheme = "https://newcss.net/theme/night.css";

function getStoredTheme() {
  try {
    return localStorage.getItem('selected-theme');
  } catch (e) {
    return null;
  }
}

function setStoredTheme(theme) {
  try {
    localStorage.setItem('selected-theme', theme);
  } catch (e) {
    console.log('Storage unavailable (private mode?)');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const themeLink = document.getElementById('theme-link');
  const toggleIcon = document.getElementById('theme-toggle');

  const savedTheme = getStoredTheme();
  if (savedTheme && themeLink) {
    themeLink.setAttribute('href', savedTheme);
  }

  if (toggleIcon && themeLink) {
    const handleThemeToggle = (e) => {
      e.preventDefault();
      
      const currentTheme = themeLink.getAttribute('href');
      const newTheme = currentTheme === lightTheme ? nightTheme : lightTheme;
      
      themeLink.setAttribute('href', newTheme);
      setStoredTheme(newTheme);
    };

    toggleIcon.addEventListener('click', handleThemeToggle);
    toggleIcon.addEventListener('touchstart', handleThemeToggle);
  }
});