document.addEventListener("DOMContentLoaded", function () {
    // Agar localStorage mein time save hai, toh woh fetch karenge
    let timeLeft = localStorage.getItem('timeLeft') ? parseInt(localStorage.getItem('timeLeft')) : 300; // 30 minutes in seconds
    const timerElement = document.getElementById("timer");

    // Time ko format karne ke liye
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${minutes}:${secs}`;
    }

    // Countdown logic
    const countdown = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(countdown);
            timerElement.textContent = "You are present!";
            timerElement.style.color = "#008000"; // Red color for "You are present!"
        } else {
            timerElement.textContent = formatTime(timeLeft);
            timeLeft--;
            localStorage.setItem('timeLeft', timeLeft); // Time ko localStorage mein store karna
        }
    }, 1000);
});
