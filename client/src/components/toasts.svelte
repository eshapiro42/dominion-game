<script>
    import { fade } from 'svelte/transition';
    
    export let socket;
    export let room = null;
    export let username = "";
    
    let newMessage = "";
    let showingToasts = [];
    let expiredToasts = [];
    let highestToastId = 0;
    let showExpiredToasts = false;

    function addMessage(text, playerMessage=false) {
        if (text == null) {
            return
        }
        var id = highestToastId;
        highestToastId += 1;
        var toast = {
            id: id,
            text: text,
            playerMessage: playerMessage,
            timeout: setTimeout(
                () => {
                    expiredToasts = expiredToasts.concat(toast);
                    showingToasts = showingToasts.filter(toast => toast.id != id);
                },
                3000
            )
        }
        showingToasts = showingToasts.concat(toast);

    }

    function cancelTimers() {
        showingToasts.forEach(toast => {
            clearTimeout(toast.timeout);
        });
    }

    function restartTimers() {
        showingToasts.forEach(toast => {
            toast.timeout = setTimeout(
                () => {
                    expiredToasts = expiredToasts.concat(toast);
                    showingToasts = showingToasts.filter(toast => toast.id != toast.id);
                },
                500 // Toasts disappear more quickly after you've moused over them
            )
        });
    }

    function sendMessage() {
        if (username == "") {
            return;
        }
        socket.emit(
            "player sent message", 
            {
                message: newMessage,
                username: username,
                room: room,
            }
        );
        newMessage = "";
    }

    function toggleExpiredToasts() {
        showExpiredToasts = !showExpiredToasts;
    }

    socket.on("message", function(data) {
        addMessage(data);
    });

    socket.on("player message", function(data) {
        addMessage(data, true);
    });

    socket.on("disconnect", 
        (reason) => {
            addMessage(`You have become disconnected from the server. Reason: ${reason}`);
        }
    );
</script>

<main>
    <i class="fa-solid fa-message"
        class:showExpiredToasts
        on:click={toggleExpiredToasts}
    ></i>

    {#if showExpiredToasts}
        <div class="expiredToasts">
            <div> 
                <!-- The things inside this div will not be reversed! -->
                {#each expiredToasts as toast}
                    <div class="toast"
                        class:playerMessage="{toast.playerMessage}"
                    >
                        {toast.text}
                    </div>
                {/each}
                <div class="messageInputs">
                    <input bind:value={newMessage} placeholder="Type a message..."/>
                    <button on:click={sendMessage}>Send Message!</button>
                </div>
            </div>
        </div>
    {/if}

    <div class="currentToasts"
        on:mouseenter={cancelTimers}
        on:mouseleave={restartTimers}
    >
        {#each showingToasts as toast (toast.id)}
            <div class="toast"
                class:playerMessage="{toast.playerMessage}"
                transition:fade
            >
                {toast.text}
            </div>
        {/each}
    </div>
</main>

<style>
    main {
        right: 5px;
        top: 5px;
        max-width: 40vw;
        position: fixed;
        text-align: right;
        z-index: 1000000000;
    }

    .currentToasts {
        margin-top: 5px;
        gap: 5px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    .toast {
        text-align: left;
        border: 1px solid slategrey;
        display: block;
        padding: 10px;
        background-color: lightpink;
        overflow-wrap: break-word;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }

    .playerMessage {
        background-color: lightblue;
    }

    .showExpiredToasts {
        color: slategrey;
    }

    .expiredToasts {
        position: sticky;
        gap: 5px;
        padding: 10px;
        height: auto;
        margin: 5px;
        max-height: 50vh;
        background-color: white;
        border: 1px solid slategrey;
        overflow-y: auto;
        display: flex;
        flex-direction: column-reverse; /* So that the newest messages are at the bottom and scroll automatically */
    }

    .fa-message {
        font-size: 30px;
    }

    .messageInputs {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        gap: 5px;
        padding-top: 10px;
    }
</style>