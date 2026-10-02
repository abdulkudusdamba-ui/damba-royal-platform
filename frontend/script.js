// Dashboard player counter
let players = 1284;

setInterval(() => {
    players += Math.floor(Math.random() * 5);

    const playerElement = document.getElementById("players");

    if (playerElement) {
        playerElement.innerHTML = players.toLocaleString();
    }
}, 3000);

// Challenge countdown timer
let time = 60;

setInterval(() => {

    const timer = document.getElementById("timer");

    if (timer && time > 0) {
        time--;
        timer.innerHTML = time;
    }

}, 1000);