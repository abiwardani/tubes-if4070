var dcTimeout = null;

$(document).ready(function () {
    namespace = '/chat';
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function () {
        console.log('connected');
        socket.emit('start');
    });

    var resetTimeout = function () {
        clearTimeout(dcTimeout);
        dcTimeout = setTimeout(function () {
            socket.emit('disconnect_request');
        }, 1000 * 60 * 5);
    };

    socket.on('bot_response', function (msg, cb) {
        // write response message to chat
        writeMessage(msg.data, isUser = false);
        stopLoadingDots();

        if (cb) {
            cb();
            socket.disconnect();
            console.log("disconnected");
        } else {
            // reset inactivity timeout
            resetTimeout();
        }
    });

    $('form#sendmsg').submit(function (event) {
        let message = $('#message').val().replace(/</g, "&lt;").replace(/>/g, "&gt;");
        writeMessage(message, isUser = true);
        if (socket.connected) {
            displayLoadingDots();
            socket.emit('send_message', { data: message });

            // reset inactivity timeout
            resetTimeout();
        }

        return false;
    });
});

function writeMessage(message, isUser) {
    // create chat bubble
    let chatTable = document.getElementById("chat");
    let responseRow = document.createElement("tr");
    let responseCell = document.createElement("td");
    let responseContent = document.createElement("p");
    let responseTimestamp = document.createElement("p");

    if (isUser) {
        responseContent.className = "userbubble";
        responseTimestamp.className = "usertime";

        // clear chat input
        let chatInput = document.getElementById("message");
        chatInput.value = "";
    } else {
        responseContent.className = "botbubble";
        responseTimestamp.className = "bottime";
    }

    // set response message
    responseContent.innerHTML = message;
    responseTimestamp.innerHTML = getDate();
    responseCell.appendChild(responseContent);
    responseCell.appendChild(responseTimestamp);
    responseRow.appendChild(responseCell);
    chatTable.appendChild(responseRow);
}

function getDate() {
    let date = new Date();
    return (date.getHours() < 10 ? '0' : '') + date.getHours() + ':' + (date.getMinutes() < 10 ? '0' : '') + date.getMinutes();
}

function displayLoadingDots() {
    let loadingDots = document.getElementsByClassName("loading-dots")[0];
    loadingDots.style.display = 'block';
}

function stopLoadingDots() {
    let loadingDots = document.getElementsByClassName("loading-dots")[0];
    loadingDots.style.display = 'none';
}