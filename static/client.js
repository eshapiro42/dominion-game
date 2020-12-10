var socket = io.connect();

var client_type = 'browser';
var username = null;
var room = null;
var room_creator = false;
var joined = false;
var startable = false;
var choice = null;
var last_message = null;

class Option {
    constructor(number, option) 
    {
        this.number = number;
        this.option = option;
    }
}

function append_message(message) {
    // Add the 'light' class to the last child of the message board
    if (last_message != null) {
        last_message.addClass('list-group-item-light');
    }
    // Add the message to the message board
    last_message = $(`<li class="list-group-item">${message}</li>`);
    $("#gameMessages").append(last_message);
    // Scroll to the bottom of the message board
    $("html, body").scrollTop($(document).height());
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
    alert(`Unable to connect to the server: ${data}.`);
});

socket.on('disconnect', function () {
    alert('You have been disconnected from the server.');
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
    $("#gameInputContainer").show(function () {
        // Focus on the input
        $("#gameInput:text:visible:first").focus();
    });
    // Allow the user to type a response and hit enter
    $("#gameInputForm").on('submit', function (event) {
        event.preventDefault();
        // Grab the response
        choice = parseInt($("#gameInput").val());
        append_message(`You entered: ${choice}.`)
        callback(choice);
        // Clear the textbox and hide the input container
        $(this).off('submit');
        $("#gameInput").val('');
        $("#gameInputContainer").hide();
    });
});

socket.on('choose yes or no', function (data, callback) {
    message = data['prompt'];
    append_message(message);
    // Show the game input container
    $("#gameInputContainer").show(function () {
        // Focus on the input
        $("#gameInput:text:visible:first").focus();
    });
    // Allow the user to type a response and hit enter
    $("#gameInputForm").on('submit', function (event) {
        event.preventDefault();
        // Grab the response
        choice = $("#gameInput").val();
        append_message(`You entered: ${choice}.`)
        callback(choice);
        // Clear the textbox and hide the input container
        $(this).off('submit');
        $("#gameInput").val('');
        $("#gameInputContainer").hide();
    });
});

socket.on('new turn', function (data, callback) {
    player = data['player'];
    // Add a horizontal rule to the message board
    $("#gameMessages").append(`<hr/>`);
    // Print out the player's name
    append_message(`<strong>${player}'s turn!</strong>`);
    // Scroll to the bottom of the message board
    $("html, body").scrollTop($(document).height());
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
        var intrigue = $('#intrigueCheckbox').prop('checked');
        var prosperity = $('#prosperityCheckbox').prop('checked');
        var distributeCost = $('#distributeCostCheckbox').prop('checked');
        var disableAttacks = $('#disableAttacksCheckbox').prop('checked');
        socket.emit(
            'start game', 
            {
                username: username, 
                room: room,
                intrigue: intrigue, 
                prosperity: prosperity,
                distributeCost: distributeCost,
                disableAttacks: disableAttacks,
            }
        );
    }
});

window.addEventListener('beforeunload', function (e) { 
    e.preventDefault(); 
    e.returnValue = ''; 
}); 
