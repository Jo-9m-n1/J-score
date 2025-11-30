"use strict";

const images = document.querySelectorAll("img");

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
