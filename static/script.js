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
