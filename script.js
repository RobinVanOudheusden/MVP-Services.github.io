// Wacht tot het DOM volledig is geladen
document.addEventListener("DOMContentLoaded", function () {
  // Selecteer alle navigatie-links
  const navLinks = document.querySelectorAll(".nav__content ul li a");
  // Selecteer de checkbox voor het hamburgermenu
  const checkbox = document.querySelector(".checkbox");

  // Voeg een click event listener toe aan elk navigatie-link
  navLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      // Schakel de checkbox (hamburgermenu) uit als deze is ingeschakeld
      if (checkbox.checked) {
        checkbox.checked = false;
      }
    });
  });
});

let slideIndex = 1;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";
  dots[slideIndex-1].className += " active";
};

const form = document.querySelector("form");

function sendEmail() {
    Email.send({
        Host : "smtp.elasticemail.com",
        Username : "robinvanoudheusden05@gmail.com",
        Password : "04A20654D5BA76A040F61B0E427E8487641F",
        To : 'robinvanoudheusden05@gmail.com',
        From : "robinvanoudheusden05@gmail.com",
        Subject : "Website Contact Form",
        Body : "New message from: " + form.name.value + "<br>Phone Number: " + form.phone.value + "<br>Email: " + form.email.value + "<br>Message: " + form.message.value + "<br>"
    })
    .then(function (message) {
        alert("Bedankt! Uw bericht is verzonden. Ik neem zo snel mogelijk contact met u op.");
    });
}

form.addEventListener("submit", (e) => {
    e.preventDefault();
    sendEmail();
});