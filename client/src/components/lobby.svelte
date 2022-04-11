<script>
    import {createEventDispatcher} from "svelte";

    import {socket} from "../stores.js";

    const dispatch = createEventDispatcher();

    let username = "";
    let room = null;
    let roomCreator = false;
    let shown = true;

    function joinedRoom(success) {
        if (success) {
            dispatch(
                "joined", 
                {
                    username: username,
                    room: room,
                    roomCreator: roomCreator,
                }
            );
            shown = false;
        }
        else {
            room = null;
            alert("Invalid username or room ID.");
        }
    }

    function setRoom(room_id) {
        room = room_id;
        joinedRoom(true);
    }

    function joinRoom() {
        if (username.length < 3) {
            alert("Username must be at least 3 characters.");
            return;
        }
        $socket.emit(
            "join room",
            {
                username: username,
                room: room,
                client_type: "browser",
            },
            joinedRoom,
        );
    }

    function createRoom() {
        if (username.length < 3) {
            alert("Username must be at least 3 characters.");
            return;
        }
        roomCreator = true;
        $socket.emit(
            "create room",
            {
                username: username,
                client_type: "browser",
            },
            setRoom,
        )
    }
</script>

{#if shown}
    <!-- Game Buttons -->
    <div class="container">
        <div class="accordion" id="gameJoinAccordion">
            <div class="accordion-item">
                <!-- Join Game Button -->
                <h2 class="accordion-header" id="headingOne">
                    <button class="accordion-button btn-link btn-lg nounderline" type="button" data-bs-toggle="collapse" data-bs-target="#joinGameCollapse" aria-expanded="true" aria-controls="joinGameCollapse">
                        Join a Game
                    </button>
                </h2>
                <!-- Join Game Collapse -->
                <div id="joinGameCollapse" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#gameJoinAccordion">
                    <div class="accordion-body text-center">
                        <div class="form-group">
                            <input type="text" class="form-control" placeholder="Your Name" autocomplete="off" bind:value={username} required>
                        </div>
                        <div class="form-group">
                            <input type="text" class="form-control" placeholder="Room ID" autocomplete="off" bind:value={room} required>
                        </div>
                        <button class="btn btn-dark" on:click={joinRoom}>Let's Move It</button>
                    </div>
                </div>
            </div>
            <div class="accordion-item">
                <!-- Create Game Button -->
                <h2 class="accordion-header" id="headingTwo">
                    <button class="accordion-button btn-link btn-lg collapsed nounderline" type="button" data-bs-toggle="collapse" data-bs-target="#createGameCollapse" aria-expanded="false" aria-controls="createGameCollapse">
                        Create a New Game
                    </button>
                </h2>
                <!-- Create Game Collapse -->
                <div id="createGameCollapse" class="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#gameJoinAccordion">
                    <div class="accordion-body text-center">
                        <div class="form-group">
                            <input type="text" class="form-control" placeholder="Your Name" bind:value={username} autocomplete="off" required>
                        </div>
                        <button class="btn btn-dark" on:click={createRoom}>Let's Groove It</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}
