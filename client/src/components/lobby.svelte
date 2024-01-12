<script>
    import {createEventDispatcher} from "svelte";

    import {socket} from "../stores.js";

    import Tabs from "./tabs.svelte";

    const dispatch = createEventDispatcher();

    let username = "";
    let room = null;
    let roomCreator = false;
    let shown = true;
    let selectedTab;

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
    <div class="panel space-above">

        <Tabs
            tabNames={
                [
                    "Join a Game",
                    "Create a Game"
                ]
            }
            bind:selectedTab={selectedTab}
        />

        {#if selectedTab == "Join a Game"}
            <div class="form-row space-above"
                on:keyup={
                    (event) => {
                        if (event.key == "Enter") {
                            joinRoom();
                        }
                    }
                }
            >
                <div class="col">
                    <input type="text" class="form-control" placeholder="Your Name" autocomplete="off" bind:value={username} required>
                </div>
                <div class="col">
                    <input type="text" class="form-control" placeholder="Room ID" autocomplete="off" bind:value={room} required>
                </div>
                <button class="space-above" on:click={joinRoom}>Let's Move It</button>
            </div>
        {:else if selectedTab == "Create a Game"}
            <div class="form-group space-above"
                on:keyup={
                    (event) => {
                        if (event.key == "Enter") {
                            createRoom();
                        }
                    }
                }
            >
                <input type="text" class="form-control" placeholder="Your Name" bind:value={username} autocomplete="off" required>
            </div>
            <button class="space-above" on:click={createRoom}>Let's Groove It</button>
        {/if}
    </div>
{/if}

<style>
    .space-above {
        margin-top: 50px;
    }

    .panel {
        left: 0px;
    }
</style>
