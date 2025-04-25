document.addEventListener("DOMContentLoaded", function () {
    let timeLeft = 300; // 30 minutes in seconds
    const timerElement = document.getElementById("timer");

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${minutes}:${secs}`;
    }

    const countdown = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(countdown);
            timerElement.textContent = "Time's up!";
            timerElement.style.color = "#ef4444"; // red
            // Optionally redirect or disable UI here
        } else {
            timerElement.textContent = formatTime(timeLeft);
            timeLeft--;
        }
    }, 1000);
});
