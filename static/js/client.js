var socket = io.connect();

var client_type = "browser";
var username = null;
var current_player = null;
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

class Card {
    constructor(name, effects, description, cost, type, quantity=null) {
        this.name = name;
        this.cost = cost;
        this.type = type;
        this.quantity = quantity;
        // Replace $ and victory points with symbols
        this.effects = effects
            .replace("$", "<i class='fas fa-coins'></i>")
            .replace("victory points", "<i class='fas fa-shield-alt'></i>")
            .replace("victory point", "<i class='fas fa-shield-alt'></i>");
        this.description = description
            .replace("$", "<i class='fas fa-coins'></i>")
            .replace("victory points", "<i class='fas fa-shield-alt'></i>")
            .replace("victory point", "<i class='fas fa-shield-alt'></i>");
        // Determine card background color
        if (this.type.includes('TREASURE')) {
            this.color = "#fff0b3";
        }
        else if (this.type.includes('VICTORY')) {
            this.color = "#c1f0c1";
        }
        else if (this.type.includes('CURSE')) {
            this.color = "#dab3ff";
        }
        else if (this.type.includes('ATTACK')) {
            this.color = "#ffcccc";
        }
        else if (this.type.includes('REACTION')) {
            this.color = "#80bfff";
        }
        // Only Supply cards have quantities
        if (this.quantity == null) {
            this.quantity = "";
        }
        // Fix infinite quantities
        else if (this.quantity == "inf") {
            this.quantity = "∞";
        }
    }
    getHTML() {
        return `
            <div class="card" style="background-color: ${this.color}">
                <div class="card-header">
                    <div class="card-title">
                        <h2>${this.name}</h2>
                    </div>
                    <div class="card-quantity">
                        <h3>${this.quantity}</h3>
                    </div>
                </div>
                <div class="card-effects">
                    <p>${this.effects}</p>
                </div>
                <div class="card-description">
                    <p>${this.description}</p>
                </div>
                <div class="card-footer">
                    <div class="card-cost">
                        <h3>${this.cost} <i class="fas fa-coins"></i></h3>
                    </div>
                    <div class="card-type">
                        <h3>${this.type}</h3>
                    </div>
                </div>
            </div>
        `;
    }
}

var chapel = new Card("Chapel", "", "Trash up to 4 cards from your hand.", 2, "Action");

function append_message(message) {
    // Add the "light" class to the last child of the message board
    if (last_message != null) {
        last_message.addClass("list-group-item-light");
    }
    // Add the message to the message board
    last_message = $(`<li class="list-group-item">${message}</li>`);
    $("#log").append(last_message);
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
        $("#gameJoinContainer").hide();
        $("#gameRoomIDContainer").show();
        if (room_creator) {
            $("#gameSetupContainer").show();
        }
        $("#gameRoomID").text(`Room ID: ${room}`);
    }
    else {
        room = null;
        alert("Invalid room ID.");
    }
}

function add_card(card_data, grid) {
    // Add a card to the specified grid
    if ("quantity" in card_data) {
        var card_html = new Card(card_data.name, card_data.effects, card_data.description, card_data.cost, card_data.type, card_data.quantity);
    }
    else {
        var card_html = new Card(card_data.name, card_data.effects, card_data.description, card_data.cost, card_data.type);
    }
    grid.append(card_html);
}

socket.on("connect", function () {
    console.log("You are connected to the server.")
});

socket.on("connect_error", function (data) {
    console.log(`Unable to connect to the server: ${data}.`);
});

socket.on("disconnect", function () {
    console.log("You have been disconnected from the server.");
});

socket.on("game startable", function (data) {
    if (room_creator) {
        startable = true;
        console.log("The game can now be started.")
    }
});

socket.on("game started", function (data) {
    console.log("GAME STARTED");
    $("#gameSetupContainer").hide();
    $(".masthead").hide();
    $("#gameRoomIDContainer").hide();
    $("#game-grid").show();
});

socket.on("message", function(data) {
    append_message(data);
});

socket.on("display supply", function(data) {
    console.log(data);
    // Clear out old stuff
    $("#supply").empty()
    // Add new stuff
    data.supply_cards.forEach(card_data => {
        var card = new Card(card_data.name, card_data.effects, card_data.description, card_data.cost, card_data.type, card_data.quantity);
        $("#supply").append(card.getHTML());
    });
});

socket.on("display hand", function(data) {
    // Clear out old stuff
    $("#hand").empty();
    // Add new stuff
    data.hand_cards.forEach(card_data => {
        var card = new Card(card_data.name, card_data.effects, card_data.description, card_data.cost, card_data.type);
        $("#hand").append(card.getHTML());
    });
});

socket.on("display played", function(data) {
    // Clear out old stuff
    $("#turn").empty();
    // Add new stuff
    data.played_cards.forEach(card_data => {
        var card = new Card(card_data.name, card_data.effects, card_data.description, card_data.cost, card_data.type);
        $("#turn").append(card.getHTML());
    });
});

socket.on("display discard", function(data) {
    // Clear out old stuff
    $("#discard").empty();
    // Add new stuff
    data.discard_cards.forEach(card_data => {
        var card = new Card(card_data.name, card_data.effects, card_data.description, card_data.cost, card_data.type);
        $("#discard").append(card.getHTML());
    });
});

socket.on("enter choice", function (data, callback) {
    message = data["prompt"];
    append_message(message);
    $(".card").on("click", function (event) {
        choice = $(this).index() + 1;
        console.log(choice);
        callback(choice);
    });


    // message = data["prompt"];
    // append_message(message);
    // // Show the game input container
    // // $("#gameInputContainer").show(function () {
    //     // Focus on the input
    //     // $("#gameInput:text:visible:first").focus();
    // // });
    // $("#game-grid").show();
    // // Allow the user to type a response and hit enter
    // $("#gameInputForm").on("submit", function (event) {
    //     event.preventDefault();
    //     // Grab the response
    //     choice = parseInt($("#gameInput").val());
    //     if (!isNaN(choice)) {            
    //         append_message(`You entered: ${choice}.`)
    //         callback(choice);
    //         // Clear the textbox and hide the input container
    //         $(this).off("submit");
    //         $("#gameInput").val("");
    //         $("#gameInputContainer").hide();
    //     }
    // });
    // ////////////////// #todo: clean up this interaction
    // $(".list-group-item:last-child tbody tr").on("click", function(event) {
    //     event.preventDefault();//#debug
    //     // Grab the response
    //     choice = parseInt(grabChoiceFromTableClick(event));
    //     if (!isNaN(choice)) {            
    //         append_message(`You entered: ${choice}.`)
    //         callback(choice);
    //         // Clear the textbox and hide the input container
    //         $(this).off("click");
    //         $("#gameInput").val("");
    //         $("#gameInputContainer").hide();
    //     }
    // });

});

function grabChoiceFromTableClick(event) {
    var row$ = $(event.target).parents("tr"),
        cell$ = row$.find("td:first-child"),
        choice = cell$.text();

    return choice;
}

socket.on("choose yes or no", function (data, callback) {
    message = data["prompt"];
    append_message(message);
    // Show the game input container
    $("#gameInputContainer").show(function () {
        // Focus on the input
        $("#gameInput:text:visible:first").focus();
    });
    // Allow the user to type a response and hit enter
    $("#gameInputForm").on("submit", function (event) {
        event.preventDefault();
        // Grab the response
        choice = $("#gameInput").val();
        append_message(`You entered: ${choice}.`)
        callback(choice);
        // Clear the textbox and hide the input container
        $(this).off("submit");
        $("#gameInput").val("");
        $("#gameInputContainer").hide();
    });
});

socket.on("new turn", function (data, callback) {
    current_player = data["player"];
    // Display the player's name on the current turn section
    $("#turn-title").empty();
    $("#turn-title").append(`<h1>${current_player}'s Turn</h1>`);
    // Add a horizontal rule to the message board
    $("#log").append(`<hr/>`);
    // Print out the player"s name
    append_message(`<strong>${current_player}'s turn!</strong>`);
    // Scroll to the bottom of the message board
    $("html, body").scrollTop($(document).height());
});


$("#createGameButton").on("click", function () {
    setTimeout(function() {
        $("#createGamePlayerNameInput:text:visible:first").focus();
    }, 100);
});

$("#createGameForm").on("submit", function (event) {
    event.preventDefault();
    username = $("#createGamePlayerNameInput").val();
    socket.emit("create room", {username: username, client_type: client_type}, set_room);
    room_creator = true;
});

$("#joinGameButton").on("click", function () {
    setTimeout(function() {
        $("#joinGamePlayerNameInput:text:visible:first").focus();
    }, 100);
});

$("#joinGameForm").on("submit", function (event) {
    event.preventDefault();
    username = $("#joinGamePlayerNameInput").val();
    room = $("#joinGameRoomID").val()
    socket.emit("join room", {username: username, room: room, client_type: client_type}, joined_room);
});

$("#addCPUButton").on("click", function () {
    socket.emit("add cpu", {room: room});
});

$("#gameStartButton").on("click", function () {
    if (!startable) {
        alert("The game cannot be started without at least two players.");
    }
    else {
        var intrigue = $("#intrigueCheckbox").prop("checked");
        var prosperity = $("#prosperityCheckbox").prop("checked");
        var distributeCost = $("#distributeCostCheckbox").prop("checked");
        var disableAttacks = $("#disableAttacksCheckbox").prop("checked");
        socket.emit(
            "start game", 
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

window.addEventListener("beforeunload", function (e) { 
    e.preventDefault(); 
    e.returnValue = ""; 
}); 


// Accordions

var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    /* Toggle between adding and removing the "active" class,
    to highlight the button that controls the panel */
    this.classList.toggle("active");

    /* Toggle between hiding and showing the active panel */
    var panel = this.nextElementSibling;
    if (panel.style.display === "block") {
      panel.style.display = "none";
    } else {
      panel.style.display = "block";
    }
  });
}


// Scrollable card-containers

var speed = 0;
var scroll = 0;
var current_container = null;
var multiplier = 6;

$('.card-container').on('mousemove', function(e) {
    current_container = $(this);
    var container_w = $(this).width();
    var mouse_x = e.pageX - $(this).offset().left;
    // console.log(mouse_x, mouse_x < 100, mouse_x > container_w - 100);
    if (mouse_x < 100 || mouse_x > container_w - 100) {
        var mouse_percent = mouse_x / container_w;
        speed = (mouse_percent - 0.5) * 2;
    }
    else {
        speed = 0;
    }
}).on ('mouseleave', function() {
    speed = 0;
});

function updatescroll(e) {
    if (current_container != null) {
        var max_scroll = current_container[0].scrollWidth - current_container.outerWidth();
        if (speed !== 0) {
            scroll += speed * multiplier;
            if (scroll < 0) {
                scroll = 0;
            }
            if (scroll > max_scroll) { 
                scroll = max_scroll;
            }
            current_container.scrollLeft(scroll);
        }
    }
    window.requestAnimationFrame(updatescroll);
}
window.requestAnimationFrame(updatescroll);