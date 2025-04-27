document.addEventListener("DOMContentLoaded", function () {
    const timerElement = document.getElementById("timer");

    const timerCompleted = localStorage.getItem('timerCompleted');
    let endTime = localStorage.getItem('timerEndTime');

    if (timerCompleted === "true") {
        timerElement.textContent = "You are present!";
        timerElement.style.color = "#008000";
        return;
    }

    if (!endTime) {
        // Naya login ke time 5 min ka timer set karo
        const now = Date.now(); // Current time in milliseconds
        endTime = now + 300 * 1000; // 5 minutes = 300000 ms
        localStorage.setItem('timerEndTime', endTime);
    } else {
        endTime = parseInt(endTime);
    }

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${minutes}:${secs}`;
    }

    const countdown = setInterval(() => {
        const now = Date.now();
        const timeLeft = Math.max(0, Math.floor((endTime - now) / 1000)); // seconds remaining

        if (timeLeft <= 0) {
            clearInterval(countdown);
            timerElement.textContent = "You are present!";
            timerElement.style.color = "#008000"; 
            localStorage.setItem('timerCompleted', 'true');
            localStorage.removeItem('timerEndTime');
        } else {
            timerElement.textContent = formatTime(timeLeft);
        }
    }, 1000);
});
