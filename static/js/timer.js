document.addEventListener("DOMContentLoaded", function () {
    const timerElement = document.getElementById("timer");

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${minutes}:${secs}`;
    }

    function startCountdown(durationInSeconds) {
        const endTime = Date.now() + durationInSeconds * 1000;
        localStorage.setItem('timerEndTime', endTime);
        localStorage.removeItem('timerCompleted');
        runTimer(endTime);
    }

    function runTimer(endTime) {
        const timerInterval = setInterval(() => {
            const now = Date.now();
            const timeLeft = Math.floor((endTime - now) / 1000);

            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                timerElement.textContent = "You are present!";
                timerElement.style.color = "#008000";
                localStorage.setItem('timerCompleted', 'true');
                localStorage.removeItem('timerEndTime');
            } else {
                timerElement.textContent = formatTime(timeLeft);
            }
        }, 1000);
    }

    function initializeTimer() {
        const timerCompleted = localStorage.getItem('timerCompleted');
        const savedEndTime = localStorage.getItem('timerEndTime');

        if (timerCompleted === 'true') {
            // Timer already completed
            timerElement.textContent = "You are present!";
            timerElement.style.color = "#008000";
        } else if (savedEndTime) {
            // Timer running, continue
            runTimer(parseInt(savedEndTime));
        } else {
            // No timer running, need to start only if login just happened
            timerElement.textContent = "Please login first!";
            timerElement.style.color = "red";
        }
    }

    initializeTimer();
});
