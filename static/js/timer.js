document.addEventListener("DOMContentLoaded", function () {
    const timerElement = document.getElementById("timer");

    let endTime = localStorage.getItem('timerEndTime');
    let timerCompleted = localStorage.getItem('timerCompleted');

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${minutes}:${secs}`;
    }

    function startTimer(endTimestamp) {
        function updateTimer() {
            const now = Date.now();
            const timeLeft = Math.floor((endTimestamp - now) / 1000);

            if (timeLeft <= 0) {
                clearInterval(countdown);
                timerElement.textContent = "You are present!";
                timerElement.style.color = "#008000";
                localStorage.setItem('timerCompleted', 'true');
                localStorage.removeItem('timerEndTime');
            } else {
                timerElement.textContent = formatTime(timeLeft);
            }
        }

        updateTimer(); // run immediately
        const countdown = setInterval(updateTimer, 1000);
    }

    if (timerCompleted === "true") {
        // Timer already complete
        timerElement.textContent = "You are present!";
        timerElement.style.color = "#008000";
    } else {
        if (!endTime) {
            // Agar timer set nahi hai (fresh login hua hai), tabhi naya timer 5 min ka start karo
            const now = Date.now();
            endTime = now + (5 * 60 * 1000); // 5 minutes in ms
            localStorage.setItem('timerEndTime', endTime);
            startTimer(endTime);
        } else {
            // Agar already timer chal raha hai (refresh case), continue karo
            startTimer(parseInt(endTime));
        }
    }
});
