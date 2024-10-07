document.addEventListener('DOMContentLoaded', function() {
    var flashMessages = JSON.parse(document.getElementById('flash-messages').textContent);
    flashMessages.forEach(function(message) {
        alert(message);
    });
});