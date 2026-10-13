// Challenge countdown timer
let time = 60;

setInterval(() => {

    const timer = document.getElementById("timer");

    if (timer && time > 0) {
        time--;
        timer.innerHTML = time;
    }

}, 1000);