<script>
    export let socket;
    export let room = null;
    export let username = null;
    export let roomJoined = false;

    let messages = [];
    let new_message = null;
    let lastId = 0;

    function addMessage(text) {
        messages = messages.concat(
            {
                text: text,
                id: lastId,
            }
        );
        lastId += 1;
    }

    function sendMessage() {
        socket.emit(
            "message", 
            {
                message: new_message,
                username: username,
                room: room,
            }
        );
    }

    socket.on("message", function(data) {
        addMessage(data);
    });
</script>

{#if roomJoined}
<main>
        <h4>Messages</h4>

        <ul class="messages">
            {#each messages as message (message.id)}
                <li>{message.text}</li>
            {:else}
                <li> No messages to show.</li>
            {/each}
        </ul>

        <input
            placeholder="What message should be sent?"
            bind:value={new_message}
        >

        <button on:click={sendMessage}>
            Send message!
        </button>
    </main>
{/if}

<style>
    main {
        margin-top: 20px;
        text-align: center;
    }

    ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }

    .messages {
        margin: 20px;
    }
    
</style>