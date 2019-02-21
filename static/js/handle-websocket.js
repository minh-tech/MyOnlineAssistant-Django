//------------------- Pop-up ask username -------------------
//const modal = document.querySelector('#myModal');
//const okBtn = document.querySelector('.ok');
//const inputName = document.querySelector('.input-name');

//---------------Websocket------------------------------
const sendButton = document.querySelector(".send");
const openButton = document.querySelector(".open");
const cancelButton = document.querySelector(".cancel");
const chatBox = document.querySelector("#myForm");
const input = document.querySelector(".text-input");
const messages = document.querySelector(".messages");

let ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
let user_id = getUserIdFromCookie();
let ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/" + user_id + "/";
console.log("Connecting to " + ws_path);
let socket = new ReconnectingWebSocket(ws_path);

//------------------- Pop-up ask username -------------------
// var username = getCookieUser("username", "Guest");

waitForSocketConnection(
    socket,
    // Join room
    () => {socket.send(JSON.stringify({
        "command": "join",
        // "username": username,
    }))}
)

//window.addEventListener(
//    'load',
//    function() {
//        if (username.toLowerCase() == "Guest") {
//            modal.style.display = "block";
//        } else {
//            modal.style.display = "none";
//
//            waitForSocketConnection(
//                socket,
//                // Join room
//                () => {socket.send(JSON.stringify({
//                    "command": "join",
//                    "username": username,
//                }))}
//            )
//        }
//    },
//    false)
//
//okBtn.addEventListener(
//    'click',
//    function() {
//        getInputName();
//    },
//    false)
//
//window.addEventListener(
//    'click',
//    function(event) {
//        if (event.target == modal) {
//            getInputName();
//        }
//    },
//    false)
//
//// Handle Enter key
//inputName.addEventListener(
//    'keypress',
//    function(e) {
//        if(e.which == 13) {
//            getInputName();
//        }
//    },
//    false);
//
//function getInputName() {
//    modal.style.display = "none";
//    username = inputName.value;
//    if (username=="") username = "Guest";
//    inputName.value = "";
//
//    addCookie("username", username, 7);
//    socket.send(JSON.stringify({
//        "command": "join",
//        "username": username,
//    }));
//}

//---------------Websocket------------------------------

// Click Send button to send message
sendButton.addEventListener(
    'click',
    function(){sendMessage();},
    false);

// Enter to send message
input.addEventListener(
    'keypress',
    function(e) {
        if(e.which == 13 && !e.shiftKey) {
            sendMessage();
            e.preventDefault();
        }
    },
    false);

function sendMessage() {
    if (input.value.trim() != "")
        socket.send(JSON.stringify({
            "command": "send",
            "message": input.value.trim(),
        }));
    input.value = "";
    return false;
}

// Handle incoming messages
socket.onmessage = function(message) {
    // Decode the JSON
    console.log("Got websocket message: " + message.data);
    let data = JSON.parse(message.data);
    // Handle errors
    if (data.error) {
        alert(data.error);
        return;
    }

    if (data.message || data.msg_type != 0) {
        switch (data.msg_type) {
            case 1:
                messages.innerHTML += "<div class='msg-container darker'>" +
                    "<span class='message'>" + data.message + "</span>" +
                    "<span class='username right'>" + data.username + "</span>" +
                    "</div>";
            break;
            case 2:
                if (!data.message.includes("|")) {
                    messages.innerHTML += "<div class='msg-container'>" +
                        "<span class='username'>" + data.username + "</span>" +
                        "<span class='message'>" + data.message + "</span>" +
                        "</div>";
                } else {
                    let sentences = data.message.split("|");
                    for (i in sentences) {
                        messages.innerHTML += "<div class='msg-container'>" +
                            "<span class='username'>" + data.username + "</span>" +
                            "<span class='message'>" + sentences[i] + "</span>" +
                            "</div>";
                    }
                }

            break;
            case 3:
                messages.innerHTML += "<div class='msg-container text-muted'>" +
                    "<span class='message'>" + data.message + "</span>" +
                    "</div>";
            break;
        }
        messages.scrollTop = messages.scrollHeight;

    } else {
        console.log("Cannot handle message!");
    }
};


//-----------------Cookie----------------------------
// Add keys and values to cookie
function addCookie(key, value, expire_days) {

    let expire_date = new Date();
    expire_date.setTime(expire_date.getTime() + (expire_days*24*60*60*1000));
    let expires = "expires=" + expire_date.toUTCString();

    console.log("Add Cookie: " + key + "=" + value + ";" + expires + ";path=/")
    document.cookie = key + "=" + value + ";" + expires + ";path=/";
}

// Get Cookie by key, set default value if key is not existed
function getCookieUser(key, default_value){
    let edited_key = key + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let objects = decodedCookie.split(';');
    for (let i = 0; i < objects.length; i++) {
        obj = objects[i];
        while (obj.charAt(0)==' ') {
            obj = obj.substring(1);
        }
        if (obj.indexOf(edited_key) == 0) {
            let value = obj.substring(edited_key.length, obj.length)
            console.log("Cookie: " + key + " = " + value);
            return value;
        }
    }
    console.log("Cookie: " + key + " = " + default_value);
    return default_value;
}

// Get User ID from cookie or create one
function getUserIdFromCookie(){
    let user_id = getCookieUser("user_id", "");
    if (user_id == "") {
        user_id = String(Date.now());
        addCookie("user_id", user_id, 7);
    }
    console.log("User id: " + user_id);

    return user_id;
}

// Wait for connecting web socket to server
function waitForSocketConnection(_socket, callback) {
    setTimeout(
        function(){
            // Check web socket connection
            if (_socket.readyState === 1) {
                console.log('Connected to chat socket')
                if (callback != null) {
                    callback()
                }
            } else {
                console.log('Wait for connection...')
                waitForSocketConnection(_socket, callback)
            }
        }, 300)
}

//waitForSocketConnection(
//    socket,
//    // Join room
//    () => {socket.send(JSON.stringify({
//        "command": "join",
//        "username": "Minh",
//    }))}
//)

openButton.onclick = function() {
    chatBox.style.display = "block";
    messages.scrollTop = messages.scrollHeight;
    input.focus()
    return false;
}

cancelButton.onclick = function() {
    chatBox.style.display = "none";
    return false;
}

// Helpful debugging
socket.onclose = function () {
    console.log("Disconnected from chat socket");
}

