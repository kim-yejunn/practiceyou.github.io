document.addEventListener('DOMContentLoaded', function() {
    var flashMessages = JSON.parse(document.getElementById('flash-messages').textContent);
    flashMessages.forEach(function(message) {
        alert(message);
    });
});
function setMobileVh() {
    let mobileVh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty("--vh", `${mobileVh}px`);
  }