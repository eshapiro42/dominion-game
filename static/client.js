var socket = io.connect('http://womboserver.duckdns.org:5000');


var client_type = 'browser';
var username = null;
var room = null;
var room_creator = false;
var joined = false;
var startable = false;
var messages = '';


class Option {
    constructor(number, option) 
    {
        this.number = number;
        this.option = option;
    }
}

function append_message(message) {
    if (message == "********************************************************************************") {
        $("#gameMessages").append(`<hr>`);
    }
    else {
        // Add the message to the message board
        $("#gameMessages").append(`<li>${message}</li>`);
    }
    // Scroll to the bottom of the message board
    $("html, body").animate({ 
        scrollTop: $( 
          'html, body').get(0).scrollHeight 
    }, 100); 
}

function set_room(room_id) {
    room = room_id;
    joined_room(true);
}

function joined_room(success) {
    if (success) {
        joined = true;
        $("#gameJoinAccordion").hide();
        $("#gameRoomIDContainer").show();
        if (room_creator) {
            $("#gameSetupContainer").show();
        }
        $("#gameRoomID").text(`Room ID: ${room}`);
    }
    else {
        room = null;
        alert('Invalid room ID.');
    }
}




socket.on('connect', function () {
    console.log('You are connected to the server.')
});

socket.on('connect_error', function (data) {
    console.log(`Unable to connect to the server: ${data}.`);
});

socket.on('disconnect', function () {
    console.log('You have been disconnected from the server.');
});

socket.on('game startable', function (data) {
    if (room_creator) {
        startable = true;
        console.log('The game can now be started.')
    }
});

socket.on('game started', function (data) {
    console.log('GAME STARTED');
    $("#gameSetupContainer").hide();
});

socket.on('message', function(data) {
    append_message(data);
});

socket.on('enter choice', function (data, callback) {
    message = data['prompt'];
    append_message(message);
    // Show the game input container
    $("#gameInputContainer").show()
    // Allow the user to type a response and hit enter
    $("#gameInput").on('keypress', function (event) {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13'){
            // Grab the response
            choice = parseInt($(this).val());
            callback(choice);
            // Clear the textbox, disable submitting and hide the input container
            $(this).val('');
            $(this).off('keypress');
            $("#gameInputContainer").hide();
        }
    });
});

socket.on('choose yes or no', function (data, callback) {
    message = data['prompt'];
    append_message(message);
    // Show the game input container
    $("#gameInputContainer").show()
    // Allow the user to type a response and hit enter
    $("#gameInput").on('keypress', function (event) {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13'){
            // Grab the response
            choice = $(this).val();
            callback(choice);
            // Clear the textbox, disable submitting and hide the input container
            $(this).val('');
            $(this).off('keypress');
            $("#gameInputContainer").hide();
        }
    });
});


$("#createGameButton").on('click', function () {
    setTimeout(function() {
        $("#createGamePlayerNameInput:text:visible:first").focus();
    }, 100);
});

$("#createGameForm").on('submit', function (event) {
    event.preventDefault();
    username = $("#createGamePlayerNameInput").val();
    socket.emit('create room', {username: username, client_type: client_type}, set_room);
    room_creator = true;
});

$("#joinGameButton").on('click', function () {
    setTimeout(function() {
        $("#joinGamePlayerNameInput:text:visible:first").focus();
    }, 100);
});

$("#joinGameForm").on('submit', function (event) {
    event.preventDefault();
    username = $("#joinGamePlayerNameInput").val();
    room = $("#joinGameRoomID").val()
    socket.emit('join room', {username: username, room: room, client_type: client_type}, joined_room);
});

$("#addCPUButton").on('click', function () {
    socket.emit('add cpu', {room: room});
});

$("#gameStartButton").on('click', function () {
    if (!startable) {
        alert('The game cannot be started without at least two players.');
    }
    else {
        socket.emit('start game', {username: username, room: room});
    }
});

window.addEventListener('beforeunload', function (e) { 
    e.preventDefault(); 
    e.returnValue = ''; 
}); 