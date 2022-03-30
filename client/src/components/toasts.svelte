<script>
    import { fade } from 'svelte/transition';
    
    export let socket;
    // export let room = null;
    // export let username = null;

    let showingToasts = [];
    let highestToastId = 0;

    function addMessage(text) {
        if (text == null) {
            return
        }
        var id = highestToastId;
        highestToastId += 1;
        var toast = {
            id: id,
            text: text,
            timeout: setTimeout(
                () => {
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
                    showingToasts = showingToasts.filter(toast => toast.id != toast.id);
                },
                500 // Toasts disappear more quickly after you've moused over them
            )
        });
    }

    // function sendMessage() {
    //     socket.emit(
    //         "message", 
    //         {
    //             message: new_message,
    //             username: username,
    //             room: room,
    //         }
    //     );
    // }

    socket.on("message", function(data) {
        addMessage(data);
    });
</script>

<main
    on:mouseenter={cancelTimers}
    on:mouseleave={restartTimers}
>
    {#each showingToasts as toast (toast.id)}
        <div class="toast"
            transition:fade
        >
            {toast.text}
        </div>
    {/each}    
</main>

<style>
    main {
        right: 5px;
        top: 5px;
        gap: 5px;
        position: fixed;
        text-align: left;
        z-index: 1000000000;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    .toast {
        border: 1px solid slategrey;
        display: block;
        padding: 10px;
        background-color: pink;
        overflow-wrap: break-word;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }
</style>